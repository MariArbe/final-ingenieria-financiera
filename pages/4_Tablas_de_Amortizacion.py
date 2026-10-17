import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.financial_math import (
    TIPOS_TASA, PERIODICIDADES, a_efectiva_anual,
    cuota_fija, tabla_cuota_fija, tabla_abono_constante,
    SISTEMAS_AMORTIZACION, ABONO_REDUCE_PLAZO, ABONO_REDUCE_CUOTA,
    tabla_amortizacion, vp_pagos_tabla, tasa_real, deflactar_tabla,
)
from utils.ui import (
    setup_page, page_header, section, kpi, callout, style_fig,
    show_plot, show_table, verification_table, empty_state, money, pct, STONE, WINE, BLUSH, ROSE, WINE_FILL,
)

setup_page("Tablas de amortización", "🧾")
page_header(
    "Tablas de amortización",
    "Construye la tabla de un crédito con cuota fija o abono constante a capital, simula abonos "
    "extraordinarios y una refinanciación, mide el costo real con inflación y comprueba que el saldo "
    "cierra en cero.",
)

SISTEMAS = SISTEMAS_AMORTIZACION
MONEY_COLS = ["Cuota", "Intereses", "Abono a capital", "Abono extra", "Pago total", "Saldo"]


def periodica(tipo_tasa, valor, m_):
    """Tasa periódica vencida equivalente a cualquier tipo de tasa."""
    return (1 + a_efectiva_anual(tipo_tasa, valor, m_)) ** (1 / m_) - 1


tab_tab, tab_mod, tab_cmp, tab_inf, tab_ver = st.tabs([
    "Tabla y gráficos", "Abonos y refinanciación", "Comparación de sistemas",
    "Inflación", "Supuestos y verificación",
])

# ---------------------------------------------------------------------------
# PARÁMETROS (columna izquierda de la primera pestaña)
# ---------------------------------------------------------------------------
with tab_tab:
    col_in, col_out = st.columns([1, 2.4], gap="large")
    with col_in:
        with st.container(border=True):
            section("Parámetros del crédito")
            capital = st.number_input("Capital ($)", min_value=1_000.0, value=50_000_000.0,
                                      step=1_000_000.0, format="%.2f", key="a_cap")
            tipo = st.selectbox("Tipo de tasa", TIPOS_TASA, index=1, key="a_tipo")
            valor_pct = st.number_input("Valor de la tasa (%)", min_value=0.0001, max_value=99.0,
                                        value=18.0, step=0.1, format="%.4f", key="a_val")
            per_nombre = st.selectbox("Periodicidad de pago", list(PERIODICIDADES), key="a_per",
                                      help="También es la periodicidad de la tasa nominal o periódica.")
            anios = st.number_input("Plazo (años)", min_value=0.25, max_value=40.0, value=5.0,
                                    step=0.25, key="a_anios")
            sistema = st.selectbox("Sistema de amortización", SISTEMAS, key="a_sis")

        m = PERIODICIDADES[per_nombre]
        ea = a_efectiva_anual(tipo, valor_pct / 100, m)
        i = (1 + ea) ** (1 / m) - 1
        n = max(1, int(round(anios * m)))

        # --- Abonos extraordinarios ---
        with st.expander("Abonos extraordinarios a capital"):
            st.caption("Pagos adicionales que van completos a capital, al final del periodo indicado.")
            abonos_df = st.data_editor(
                pd.DataFrame({"Periodo": pd.Series(dtype="int"), "Monto ($)": pd.Series(dtype="float")}),
                num_rows="dynamic", key="a_abonos", hide_index=True,
                column_config={
                    "Periodo": st.column_config.NumberColumn(min_value=1, max_value=n, step=1, format="%d"),
                    "Monto ($)": st.column_config.NumberColumn(min_value=0.0, format="$%.2f"),
                },
            )
            modo_abono = st.radio(
                "Después de cada abono", [ABONO_REDUCE_PLAZO, ABONO_REDUCE_CUOTA], key="a_modo",
                help="Reducir plazo: se mantiene la cuota y el crédito termina antes. "
                     "Reducir cuota: se mantiene el plazo y la cuota se recalcula sobre el nuevo saldo.",
            )

        abonos = {}
        for _, fila in abonos_df.dropna().iterrows():
            k_ab, monto = int(fila["Periodo"]), float(fila["Monto ($)"])
            if 1 <= k_ab <= n and monto > 0:
                abonos[k_ab] = abonos.get(k_ab, 0.0) + monto

        # --- Refinanciación ---
        refi = None
        with st.expander("Refinanciación a mitad de camino"):
            if n < 2:
                st.caption("Se necesitan al menos 2 cuotas para refinanciar.")
            else:
                usar_refi = st.toggle("Refinanciar el crédito", key="a_refi_on")
                k_refi = st.number_input("Refinanciar después de la cuota", min_value=1, max_value=n - 1,
                                         value=max(1, n // 2), step=1, key="a_refi_k",
                                         disabled=not usar_refi)
                tasa_refi_pct = st.number_input(f"Nueva tasa (%, {tipo.lower()})", min_value=0.0001,
                                                max_value=99.0, value=round(valor_pct * 0.8, 4),
                                                step=0.1, format="%.4f", key="a_refi_tasa",
                                                disabled=not usar_refi)
                plazo_refi = st.radio("Plazo después de refinanciar",
                                      ["Conservar las cuotas pendientes", "Definir nuevo número de cuotas"],
                                      key="a_refi_plazo", disabled=not usar_refi)
                cuotas_refi = None
                if plazo_refi == "Definir nuevo número de cuotas":
                    cuotas_refi = st.number_input("Cuotas restantes tras refinanciar", min_value=1,
                                                  max_value=600, value=max(1, n - int(k_refi)), step=1,
                                                  key="a_refi_n", disabled=not usar_refi)
                if usar_refi:
                    i_refi = periodica(tipo, tasa_refi_pct / 100, m)
                    refi = {"periodo": int(k_refi), "tasa": i_refi, "cuotas": cuotas_refi}

    hay_mod = bool(abonos) or refi is not None
    opciones = dict(abonos_extra=abonos, modo_abono=modo_abono, refinanciacion=refi)

    # Escenario base (sin abonos ni refinanciación) y escenario modificado, para ambos sistemas
    base = {s: tabla_amortizacion(capital, i, n, s) for s in SISTEMAS}
    tablas = {s: tabla_amortizacion(capital, i, n, s, **opciones) for s in SISTEMAS}
    df = tablas[sistema]
    df_base = base[sistema]
    intereses = df["Intereses"].sum()
    total = df["Pago total"].sum()

    with col_out:
        if hay_mod:
            partes = []
            if abonos:
                partes.append(f"{len(abonos)} abono(s) extraordinario(s) por {money(sum(abonos.values()))} "
                              f"({modo_abono.lower()})")
            if refi:
                partes.append(f"refinanciación después de la cuota {refi['periodo']}")
            callout("Escenario con " + " y ".join(partes) + ". Mira el impacto en la pestaña "
                    "«Abonos y refinanciación».", "info")

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            kpi("Efectiva anual", pct(ea), f"Periódica: {pct(i)}")
        with k2:
            kpi("Primera cuota", money(df["Cuota"].iloc[0], 2), f"{len(df)} cuotas en total")
        with k3:
            kpi("Intereses totales", money(intereses), f"{intereses / capital * 100:.1f}% del capital")
        with k4:
            kpi("Total pagado", money(total), sistema, accent=True)

        st.write("")
        fig = go.Figure()
        if hay_mod:
            fig.add_scatter(x=[0] + df_base["Periodo"].tolist(), y=[capital] + df_base["Saldo"].tolist(),
                            mode="lines", name="Sin abonos ni refinanciación",
                            line=dict(color=STONE, width=2, dash="dash"))
        fig.add_scatter(x=[0] + df["Periodo"].tolist(), y=[capital] + df["Saldo"].tolist(), mode="lines",
                        name="Saldo", line=dict(color=WINE, width=3), fill="tozeroy",
                        fillcolor=WINE_FILL)
        fig.update_yaxes(tickprefix="$", tickformat=",.0f")
        style_fig(fig, "Saldo de la deuda", f"Periodo ({per_nombre.lower()})", "Saldo (COP)")
        fig.update_layout(showlegend=hay_mod, height=300)
        show_plot(fig)

        fig2 = go.Figure()
        fig2.add_bar(x=df["Periodo"], y=df["Intereses"], name="Intereses", marker_color=STONE)
        fig2.add_bar(x=df["Periodo"], y=df["Abono a capital"], name="Abono a capital", marker_color=WINE)
        if abonos:
            fig2.add_bar(x=df["Periodo"], y=df["Abono extra"], name="Abono extra", marker_color=BLUSH)
        fig2.update_layout(barmode="stack")
        fig2.update_yaxes(tickprefix="$", tickformat=",.0f")
        style_fig(fig2, "Composición del pago", f"Periodo ({per_nombre.lower()})", "Pago (COP)")
        show_plot(fig2)

    # La tabla va a todo el ancho: tiene 8 columnas y así se lee sin desplazarse de lado
    st.write("")
    section("Tabla de amortización", sistema)
    col_cfg = {c: st.column_config.NumberColumn(format="$%.2f") for c in MONEY_COLS}
    col_cfg["Tasa periódica"] = st.column_config.NumberColumn(format="percent")
    show_table(df, column_config=col_cfg)
    st.download_button("Descargar tabla (CSV)", df.to_csv(index=False).encode("utf-8"),
                       file_name="tabla_amortizacion.csv", mime="text/csv")

# ---------------------------------------------------------------------------
# ABONOS Y REFINANCIACIÓN
# ---------------------------------------------------------------------------
with tab_mod:
    if not hay_mod:
        empty_state("Aún no hay abonos ni refinanciación",
                    "Configúralos en la pestaña «Tabla y gráficos», en los desplegables debajo de los "
                    "parámetros del crédito, y aquí verás cuánto cambian los intereses y el plazo.")
    else:
        int_base, int_mod = df_base["Intereses"].sum(), intereses
        tot_base = df_base["Pago total"].sum()
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            kpi("Intereses ahorrados", money(int_base - int_mod),
                f"{(int_base - int_mod) / int_base * 100:.1f}% de los intereses originales", accent=True)
        with k2:
            kpi("Número de cuotas", f"{len(df)}", f"Antes: {len(df_base)} ({len(df) - len(df_base):+d})")
        with k3:
            kpi("Total pagado", money(total), f"Antes: {money(tot_base)}")
        with k4:
            kpi("Última cuota", money(df["Cuota"].iloc[-1], 2), f"Antes: {money(df_base['Cuota'].iloc[-1], 2)}")

        textos = []
        if abonos:
            textos.append(
                f"Los abonos extraordinarios suman {money(sum(abonos.values()))} y, con la opción "
                f"«{modo_abono.lower()}», "
                + ("acortan el crédito porque la cuota se mantiene y cada peso extra deja de causar intereses."
                   if modo_abono == ABONO_REDUCE_PLAZO else
                   "bajan la cuota y conservan el plazo; se ahorra menos interés que reduciendo plazo, "
                   "porque el saldo baja más despacio.")
            )
        if refi:
            fila_post = df[df["Periodo"] == refi["periodo"] + 1]
            if not fila_post.empty:
                textos.append(
                    f"Después de la cuota {refi['periodo']} la tasa periódica pasa de {pct(i)} a "
                    f"{pct(refi['tasa'])} (EA {pct((1 + refi['tasa']) ** m - 1)}) y la cuota queda en "
                    f"{money(fila_post['Cuota'].iloc[0], 2)}."
                )
        if int_mod > int_base:
            textos.append("Ojo: este escenario paga más intereses que el original, normalmente porque la "
                          "refinanciación alarga el plazo o sube la tasa.")
        callout(" ".join(textos), "info")

        c1, c2 = st.columns(2, gap="large")
        with c1:
            fig = go.Figure()
            fig.add_scatter(x=df_base["Periodo"], y=df_base["Pago total"], name="Original", mode="lines",
                            line=dict(color=STONE, width=3))
            fig.add_scatter(x=df["Periodo"], y=df["Pago total"], name="Con cambios", mode="lines",
                            line=dict(color=WINE, width=3))
            fig.update_yaxes(tickprefix="$", tickformat=",.0f")
            style_fig(fig, "Pago por periodo", f"Periodo ({per_nombre.lower()})", "Pago (COP)")
            show_plot(fig)
        with c2:
            fig = go.Figure()
            fig.add_scatter(x=df_base["Periodo"], y=df_base["Intereses"].cumsum(), name="Original",
                            mode="lines", line=dict(color=STONE, width=3))
            fig.add_scatter(x=df["Periodo"], y=df["Intereses"].cumsum(), name="Con cambios", mode="lines",
                            line=dict(color=WINE, width=3))
            fig.update_yaxes(tickprefix="$", tickformat=",.0f")
            style_fig(fig, "Intereses acumulados", f"Periodo ({per_nombre.lower()})", "Intereses (COP)")
            show_plot(fig)

        section("Resumen de escenarios", sistema)
        show_table(pd.DataFrame([
            {"Escenario": "Original", "Cuotas": len(df_base),
             "Primera cuota": money(df_base["Cuota"].iloc[0], 2),
             "Intereses totales": money(int_base, 2), "Total pagado": money(tot_base, 2)},
            {"Escenario": "Con abonos / refinanciación", "Cuotas": len(df),
             "Primera cuota": money(df["Cuota"].iloc[0], 2),
             "Intereses totales": money(int_mod, 2), "Total pagado": money(total, 2)},
        ]))

# ---------------------------------------------------------------------------
# COMPARACIÓN DE SISTEMAS
# ---------------------------------------------------------------------------
with tab_cmp:
    if hay_mod:
        st.caption("Ambos sistemas incluyen los mismos abonos extraordinarios y la misma refinanciación.")
    resumen = []
    for nombre, t in tablas.items():
        resumen.append({
            "Sistema": nombre,
            "Cuotas": len(t),
            "Primera cuota": money(t["Cuota"].iloc[0], 2),
            "Última cuota": money(t["Cuota"].iloc[-1], 2),
            "Intereses totales": money(t["Intereses"].sum(), 2),
            "Total pagado": money(t["Pago total"].sum(), 2),
        })
    show_table(pd.DataFrame(resumen))

    int_cf, int_ac = tablas[SISTEMAS[0]]["Intereses"].sum(), tablas[SISTEMAS[1]]["Intereses"].sum()
    callout(
        f"El abono constante paga {money(int_cf - int_ac)} menos en intereses que la cuota fija, "
        f"pero su primera cuota es {money(tablas[SISTEMAS[1]]['Cuota'].iloc[0] - tablas[SISTEMAS[0]]['Cuota'].iloc[0])} "
        "más alta. La cuota fija es más fácil de presupuestar; el abono constante es más barato en total."
        if int_cf - int_ac > 0.005 else
        "Con una sola cuota (o un abono que liquida el crédito) los dos sistemas coinciden."
        if abs(int_cf - int_ac) <= 0.005 else
        "Con estos parámetros la cuota fija resulta más barata en intereses totales.",
        "info",
    )

    c1, c2 = st.columns(2, gap="large")
    with c1:
        fig = go.Figure()
        for nombre, color in zip(SISTEMAS, [WINE, STONE]):
            fig.add_scatter(x=tablas[nombre]["Periodo"], y=tablas[nombre]["Cuota"], name=nombre,
                            mode="lines", line=dict(color=color, width=3))
        fig.update_yaxes(tickprefix="$", tickformat=",.0f")
        style_fig(fig, "Cuota por periodo", f"Periodo ({per_nombre.lower()})", "Cuota (COP)")
        show_plot(fig)
    with c2:
        fig = go.Figure()
        for nombre, color in zip(SISTEMAS, [WINE, STONE]):
            t = tablas[nombre]
            fig.add_scatter(x=[0] + t["Periodo"].tolist(), y=[capital] + t["Saldo"].tolist(), name=nombre,
                            mode="lines", line=dict(color=color, width=3))
        fig.update_yaxes(tickprefix="$", tickformat=",.0f")
        style_fig(fig, "Saldo por periodo", f"Periodo ({per_nombre.lower()})", "Saldo (COP)")
        show_plot(fig)

# ---------------------------------------------------------------------------
# INFLACIÓN
# ---------------------------------------------------------------------------
with tab_inf:
    col_pi, col_txt = st.columns([1, 2.4], gap="large")
    with col_pi:
        with st.container(border=True):
            section("Supuesto de inflación")
            infl_pct = st.number_input("Inflación anual esperada (%, EA)", min_value=-10.0, max_value=99.0,
                                       value=5.0, step=0.25, format="%.2f", key="a_infl",
                                       help="Se supone constante durante todo el crédito.")
    infl = infl_pct / 100
    pi_p = (1 + infl) ** (1 / m) - 1
    r_p = tasa_real(i, pi_p)
    r_ea = tasa_real(ea, infl)
    dfl = deflactar_tabla(df, pi_p)
    total_real = dfl["Pago en pesos de hoy"].sum()
    int_real = total_real - capital

    with col_txt:
        ult = dfl.iloc[-1]
        texto = (f"Con una inflación de {infl_pct:.2f}% anual, la última cuota de {money(ult['Pago nominal'], 2)} "
                 f"equivale a {money(ult['Pago en pesos de hoy'], 2)} de hoy. ")
        if refi:
            texto += (f"Después de la refinanciación la tasa real pasa a "
                      f"{pct(tasa_real((1 + refi['tasa']) ** m - 1, infl), 2)} EA. ")
        if r_ea < 0:
            texto += "La tasa real es negativa: la inflación supera la tasa del crédito y el deudor devuelve " \
                     "menos poder adquisitivo del que recibió."
        elif infl < 0:
            texto += "Con deflación cada cuota futura pesa más que hoy: el crédito se encarece en términos reales."
        else:
            texto += "La inflación abarata el crédito en términos reales, sobre todo las cuotas más lejanas."
        callout(texto, "info")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi("Tasa real EA", pct(r_ea, 2), f"Periódica: {pct(r_p)}")
    with k2:
        kpi("Total pagado", money(total), "Pesos nominales")
    with k3:
        kpi("Total en pesos de hoy", money(total_real),
            f"{abs(1 - total_real / total) * 100:.1f}% {'menos' if total_real <= total else 'más'}", accent=True)
    with k4:
        kpi("Intereses reales", money(int_real), f"vs {money(intereses)} nominales")
    st.write("")

    fig = go.Figure()
    fig.add_scatter(x=dfl["Periodo"], y=dfl["Pago nominal"], name="Pago nominal", mode="lines",
                    line=dict(color=STONE, width=3))
    fig.add_scatter(x=dfl["Periodo"], y=dfl["Pago en pesos de hoy"], name="Pago en pesos de hoy",
                    mode="lines", line=dict(color=WINE, width=3))
    fig.update_yaxes(tickprefix="$", tickformat=",.0f")
    style_fig(fig, "Pagos nominales vs. pesos constantes", f"Periodo ({per_nombre.lower()})", "Pago (COP)")
    show_plot(fig)

    section("Tabla en pesos de hoy", f"{sistema}, inflación periódica {pct(pi_p)}")
    show_table(dfl, column_config={c: st.column_config.NumberColumn(format="$%.2f")
                                   for c in dfl.columns if c != "Periodo"})
    st.download_button("Descargar tabla en pesos de hoy (CSV)", dfl.to_csv(index=False).encode("utf-8"),
                       file_name="tabla_pesos_constantes.csv", mime="text/csv")

# ---------------------------------------------------------------------------
# SUPUESTOS Y VERIFICACIÓN
# ---------------------------------------------------------------------------
with tab_ver:
    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        with st.container(border=True):
            section("Supuestos")
            st.markdown(
                f"- **Tipo de tasa de entrada:** {tipo.lower()}, convertida a EA y luego a tasa periódica vencida.\n"
                f"- **Periodicidad de pago:** {per_nombre.lower()} ({m} pagos por año).\n"
                f"- **Número de cuotas:** plazo en años × pagos por año, redondeado ({n}).\n"
                "- **Pagos:** al final de cada periodo (cuota vencida).\n"
                "- **Intereses del periodo:** saldo anterior × tasa periódica.\n"
                "- **Abonos extraordinarios:** se pagan al final del periodo, junto con la cuota, y van "
                "completos a capital; reducen el plazo o la cuota según la opción elegida.\n"
                "- **Refinanciación:** después de la cuota indicada, el saldo se reprograma a la nueva tasa "
                "(convertida igual que la original) en las cuotas indicadas.\n"
                "- **Inflación:** constante; la anual se convierte a periódica y los pagos se llevan a pesos "
                "de hoy dividiendo por (1 + π)^k."
            )
    with col_b:
        with st.container(border=True):
            section("Fórmulas empleadas")
            st.latex(r"i=(1+EA)^{1/m}-1")
            st.latex(r"\text{Cuota fija: } A=P\,\frac{i}{1-(1+i)^{-n}}")
            st.latex(r"\text{Abono constante: } K=\frac{P}{n},\quad \text{Cuota}_k=K+i\,S_{k-1}")
            st.latex(r"\text{Tras abono o refinanciación: } A'=S_k\,\frac{i'}{1-(1+i')^{-r}}")
            st.latex(r"\text{Cuotas pendientes: } r=\left\lceil\frac{-\ln(1-S_k\,i/A)}{\ln(1+i)}\right\rceil")
            st.latex(r"\text{Fisher: } 1+i=(1+r)(1+\pi),\quad \text{Pago real}_k=\frac{\text{Pago}_k}{(1+\pi)^k}")

    st.write("")
    section("Verificación contra cálculo manual",
            "Se comprueban los dos sistemas sin cambios, el escenario con abonos o refinanciación y la "
            "conversión a pesos de hoy.")
    t_cf, t_ac = base[SISTEMAS[0]], base[SISTEMAS[1]]
    filas = [
        ("Cuota fija: coincide con la tabla original (máx. diferencia de saldo)",
         float((t_cf["Saldo"] - tabla_cuota_fija(capital, i, n)["Saldo"]).abs().max()), 0.0, capital),
        ("Cuota fija: cuota = P·i/(1−(1+i)^−n)", t_cf["Cuota"].iloc[0], capital * i / (1 - (1 + i) ** -n)),
        ("Cuota fija: ajuste de la última cuota", t_cf["Cuota"].iloc[-1], cuota_fija(capital, i, n), capital),
        ("Cuota fija: suma de abonos = capital", t_cf["Abono a capital"].sum(), capital),
        ("Cuota fija: saldo final = 0", t_cf["Saldo"].iloc[-1], 0.0, capital),
        ("Cuota fija: VP de las cuotas = capital", vp_pagos_tabla(t_cf), capital),
        ("Abono constante: coincide con la tabla original (máx. diferencia de saldo)",
         float((t_ac["Saldo"] - tabla_abono_constante(capital, i, n)["Saldo"]).abs().max()), 0.0, capital),
        ("Abono constante: suma de abonos = capital", t_ac["Abono a capital"].sum(), capital),
        ("Abono constante: saldo final = 0", t_ac["Saldo"].iloc[-1], 0.0, capital),
        ("Abono constante: VP de las cuotas = capital", vp_pagos_tabla(t_ac), capital),
    ]
    if hay_mod:
        filas += [
            ("Escenario: abonos ordinarios + extra = capital",
             df["Abono a capital"].sum() + df["Abono extra"].sum(), capital),
            ("Escenario: saldo final = 0", df["Saldo"].iloc[-1], 0.0, capital),
            ("Escenario: VP de los pagos (tasa de cada periodo) = capital", vp_pagos_tabla(df), capital),
        ]
    # Factor de descuento real acumulado: Π(1 + r_j), con r_j la tasa real de cada periodo
    tasas_reales = tasa_real(df["Tasa periódica"].to_numpy(), pi_p)
    vp_real = float((dfl["Pago en pesos de hoy"].to_numpy() / (1 + tasas_reales).cumprod()).sum())
    filas += [
        ("Total pagado = capital + intereses (sistema elegido)", total, capital + intereses),
        ("Fisher: (1 + r)(1 + π) = 1 + i", (1 + r_p) * (1 + pi_p), 1 + i),
        ("Pagos en pesos de hoy, descontados a la tasa real, = capital", vp_real, capital),
    ]
    verification_table(filas, tol=1e-6)
