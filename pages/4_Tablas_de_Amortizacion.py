import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.financial_math import (
    TIPOS_TASA, PERIODICIDADES, a_efectiva_anual,
    cuota_fija, tabla_cuota_fija, tabla_abono_constante, factor_vp_serie,
)
from utils.ui import (
    setup_page, page_header, section, kpi, callout, style_fig,
    show_plot, show_table, verification_table, money, pct, STONE, WINE, BLUSH,
)

setup_page("Tablas de amortización", "🧾")
page_header(
    "Tablas de amortización",
    "Construye la tabla de un crédito con cuota fija o abono constante a capital, compara los dos "
    "sistemas y comprueba que el saldo cierra en cero.",
)

SISTEMAS = ["Cuota fija", "Abono constante a capital"]

tab_tab, tab_cmp, tab_ver = st.tabs(["Tabla y gráficos", "Comparación de sistemas", "Supuestos y verificación"])

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

    tablas = {
        SISTEMAS[0]: tabla_cuota_fija(capital, i, n),
        SISTEMAS[1]: tabla_abono_constante(capital, i, n),
    }
    df = tablas[sistema]
    intereses = df["Intereses"].sum()
    total = df["Cuota"].sum()

    with col_out:
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            kpi("Efectiva anual", pct(ea), f"Periódica: {pct(i)}")
        with k2:
            kpi("Primera cuota", money(df["Cuota"].iloc[0], 2), f"{n} cuotas en total")
        with k3:
            kpi("Intereses totales", money(intereses), f"{intereses / capital * 100:.1f}% del capital")
        with k4:
            kpi("Total pagado", money(total), sistema, accent=True)

        st.write("")
        periodos = [0] + df["Periodo"].tolist()
        fig = go.Figure()
        fig.add_scatter(x=periodos, y=[capital] + df["Saldo"].tolist(), mode="lines", name="Saldo",
                        line=dict(color=WINE, width=3), fill="tozeroy", fillcolor="rgba(136,19,55,0.10)")
        fig.update_yaxes(tickprefix="$", tickformat=",.0f")
        style_fig(fig, "Saldo de la deuda", f"Periodo ({per_nombre.lower()})", "Saldo (COP)")
        fig.update_layout(showlegend=False, height=300)
        show_plot(fig)

        fig2 = go.Figure()
        fig2.add_bar(x=df["Periodo"], y=df["Intereses"], name="Intereses", marker_color=STONE)
        fig2.add_bar(x=df["Periodo"], y=df["Abono a capital"], name="Abono a capital", marker_color=WINE)
        fig2.update_layout(barmode="stack")
        fig2.update_yaxes(tickprefix="$", tickformat=",.0f")
        style_fig(fig2, "Composición de la cuota", f"Periodo ({per_nombre.lower()})", "Cuota (COP)")
        show_plot(fig2)

        section("Tabla de amortización", sistema)
        money_cols = ["Cuota", "Intereses", "Abono a capital", "Saldo"]
        show_table(df, column_config={c: st.column_config.NumberColumn(format="$%.2f") for c in money_cols})
        st.download_button("Descargar tabla (CSV)", df.to_csv(index=False).encode("utf-8"),
                           file_name="tabla_amortizacion.csv", mime="text/csv")

# ---------------------------------------------------------------------------
# COMPARACIÓN
# ---------------------------------------------------------------------------
with tab_cmp:
    resumen = []
    for nombre, t in tablas.items():
        resumen.append({
            "Sistema": nombre,
            "Primera cuota": money(t["Cuota"].iloc[0], 2),
            "Última cuota": money(t["Cuota"].iloc[-1], 2),
            "Intereses totales": money(t["Intereses"].sum(), 2),
            "Total pagado": money(t["Cuota"].sum(), 2),
        })
    show_table(pd.DataFrame(resumen))

    int_cf, int_ac = tablas[SISTEMAS[0]]["Intereses"].sum(), tablas[SISTEMAS[1]]["Intereses"].sum()
    callout(
        f"El abono constante paga {money(int_cf - int_ac)} menos en intereses que la cuota fija, "
        f"pero su primera cuota es {money(tablas[SISTEMAS[1]]['Cuota'].iloc[0] - tablas[SISTEMAS[0]]['Cuota'].iloc[0])} "
        "más alta. La cuota fija es más fácil de presupuestar; el abono constante es más barato en total."
        if int_cf >= int_ac else
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
                "- **Intereses del periodo:** saldo anterior × tasa periódica."
            )
    with col_b:
        with st.container(border=True):
            section("Fórmulas empleadas")
            st.latex(r"i=(1+EA)^{1/m}-1\qquad \text{Cuota fija: } A=P\,\frac{i}{1-(1+i)^{-n}}")
            st.latex(r"\text{Abono constante: } K=\frac{P}{n}\qquad \text{Cuota}_k=K+i\,S_{k-1}")

    st.write("")
    section("Verificación contra cálculo manual", "Se comprueban los dos sistemas con los parámetros actuales.")
    t_cf, t_ac = tablas[SISTEMAS[0]], tablas[SISTEMAS[1]]
    filas = [
        ("Cuota fija: suma de abonos = capital", t_cf["Abono a capital"].sum(), capital),
        ("Cuota fija: saldo final = 0", t_cf["Saldo"].iloc[-1], 0.0),
        ("Cuota fija: cuota = P·i/(1−(1+i)^−n)", t_cf["Cuota"].iloc[0], capital * i / (1 - (1 + i) ** -n)),
        ("Cuota fija: VP de las cuotas = capital",
         sum(c / (1 + i) ** k for k, c in zip(t_cf["Periodo"], t_cf["Cuota"])), capital),
        ("Abono constante: suma de abonos = capital", t_ac["Abono a capital"].sum(), capital),
        ("Abono constante: saldo final = 0", t_ac["Saldo"].iloc[-1], 0.0),
        ("Abono constante: VP de las cuotas = capital",
         sum(c / (1 + i) ** k for k, c in zip(t_ac["Periodo"], t_ac["Cuota"])), capital),
        ("Total pagado = capital + intereses (sistema elegido)", total, capital + intereses),
    ]
    verification_table(filas, tol=1e-6)