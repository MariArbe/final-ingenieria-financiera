import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.casos import (
    DEFAULTS, TEMAS_POR_CASO, _oferta, calcular_caso1, calcular_caso2, calcular_caso3, calcular_casos,
    decision_caso2, primera_cuota_requerida, vf_gradiente_formula,
)
from utils.financial_math import TIPOS_TASA, PERIODICIDADES, cuota_fija, factor_vf_serie, vf_flujos
from utils.ui import (
    setup_page, page_header, section, kpi, callout, style_fig,
    show_plot, show_table, verification_table, money, pct, STONE, WINE, BLUSH,
)

setup_page("Casos aplicados", "🧭")
page_header(
    "Casos aplicados",
    "Tres casos con productos financieros: invertir, endeudarse y ahorrar para una meta. "
    "Cambia los datos y mira cómo cambia la decisión.",
)

d1, d2, d3 = DEFAULTS["c1"], DEFAULTS["c2"], DEFAULTS["c3"]
PALETA = [WINE, STONE, BLUSH]

# ---------------------------------------------------------------------------
# PERSISTENCIA DE LOS DATOS
# Streamlit borra el valor de un campo cuando se sale de la página donde está. Por eso cada
# campo se guarda también en una copia propia ("_keep_<clave>") que no se borra, y al volver a
# esta página se restaura desde ahí. Los campos no reciben `value=`: lo toman de la sesión.
# ---------------------------------------------------------------------------
CAMPOS = {
    "c1_fuente": d1["fuente"], "c1_fecha": d1["fecha"], "c1_cap": d1["cap"], "c1_meses": d1["meses"],
    "c1_ret": d1["ret"], "c1_ct": d1["cdt_tipo"], "c1_cv": d1["cdt_val"], "c1_cp": d1["cdt_per"],
    "c1_ah": d1["ah_ea"], "c1_ahc": d1["ah_costo"], "c1_inf": d1["infl"], "c1_pts": d1["pts"],
    "c2_fuente": d2["fuente"], "c2_fecha": d2["fecha"], "c2_cap": d2["cap"], "c2_anios": d2["anios"],
    "c2_a_n": d2["a_nombre"], "c2_a_t": d2["a_tipo"], "c2_a_v": d2["a_val"], "c2_a_p": d2["a_per"],
    "c2_b_n": d2["b_nombre"], "c2_b_t": d2["b_tipo"], "c2_b_v": d2["b_val"], "c2_b_p": d2["b_per"],
    "c3_fuente": d3["fuente"], "c3_fecha": d3["fecha"], "c3_meta": d3["meta"], "c3_meses": d3["meses"],
    "c3_ea": d3["ea"], "c3_grad": d3["grad"], "c3_ga": d3["g_arit"], "c3_gg": d3["g_geom"],
}
for clave, inicial in CAMPOS.items():
    if clave not in st.session_state:
        st.session_state[clave] = st.session_state.get("_keep_" + clave, inicial)


def guardar_campos():
    for clave in CAMPOS:
        if clave in st.session_state:
            st.session_state["_keep_" + clave] = st.session_state[clave]


tab1, tab2, tab3, tab_res, tab_ver = st.tabs([
    "Caso 1 · CDT vs. ahorros", "Caso 2 · Crédito", "Caso 3 · Plan de ahorro", "Resumen",
    "Supuestos y verificación",
])

# ---------------------------------------------------------------------------
# CASO 1
# ---------------------------------------------------------------------------
with tab1:
    col_in, col_out = st.columns([1, 2.4], gap="large")
    with col_in:
        with st.container(border=True):
            section("Datos del caso", "Dónde invertir el mismo capital durante el plazo.")
            fuente1 = st.text_input("Fuente de los datos", key="c1_fuente")
            fecha1 = st.text_input("Fecha de consulta", key="c1_fecha")
            cap1 = st.number_input("Capital a invertir ($)", min_value=1.0, step=500_000.0, key="c1_cap")
            meses1 = st.slider("Plazo (meses)", 1, 60, key="c1_meses")
            ret1 = st.number_input("Retención en la fuente (%)", min_value=0.0, max_value=100.0,
                                   step=0.5, key="c1_ret", help="Se aplica sobre los rendimientos al vencimiento.")
        with st.container(border=True):
            section("CDT")
            cdt_tipo = st.selectbox("Tipo de tasa", TIPOS_TASA, key="c1_ct")
            cdt_val = st.number_input("Valor de la tasa (%)", min_value=0.0001, max_value=99.0,
                                      step=0.1, format="%.4f", key="c1_cv")
            cdt_per = st.selectbox("Periodicidad", list(PERIODICIDADES), key="c1_cp")
        with st.container(border=True):
            section("Otras alternativas")
            ah_ea = st.number_input("Cuenta de ahorros (EA %)", min_value=0.0, step=0.05, format="%.2f", key="c1_ah")
            ah_costo = st.number_input("Cuota de manejo de la cuenta ($ por mes)", min_value=0.0, step=500.0,
                                       key="c1_ahc", help="Costo del medio de manejo (tarjeta débito).")
            infl1 = st.number_input("Inflación esperada (EA %)", min_value=0.0, step=0.1, key="c1_inf")
            pts1 = st.number_input("Puntos adicionales (EA %)", min_value=0.0, step=0.1, key="c1_pts")

    p1 = dict(cap=cap1, meses=meses1, cdt_tipo=cdt_tipo, cdt_val=cdt_val, cdt_per=cdt_per, ah_ea=ah_ea,
              ah_costo=ah_costo, ret=ret1, infl=infl1, pts=pts1, fuente=fuente1, fecha=fecha1)
    r1 = calcular_caso1(p1)

    with col_out:
        cols = st.columns(3)
        for col, pr in zip(cols, r1["prods"]):
            with col:
                kpi(pr["nombre"], pct(pr["ea_neta"], 2), f"EA neta · bruta {pct(pr['ea'], 2)}",
                    accent=pr is r1["mejor"])
        st.write("")
        tabla = pd.DataFrame({
            "Concepto": ["Intereses brutos", "Retención", "Cuota de manejo", "Ganancia neta", "Valor final"],
            **{pr["nombre"]: [money(pr["bruto"]), money(pr["retencion"]), money(pr["costos"]),
                              money(pr["neto"]), money(pr["vf"])]
               for pr in r1["prods"]},
        })
        show_table(tabla)

        fig = go.Figure()
        for pr, color in zip(r1["prods"], PALETA):
            xs = list(range(1, 61))
            ys = [cap1 + (cap1 * ((1 + pr["ea"]) ** (mm / 12) - 1)) * (1 - ret1 / 100) - pr["costo_mes"] * mm
                  for mm in xs]
            fig.add_scatter(x=xs, y=ys, name=pr["nombre"], mode="lines", line=dict(color=color, width=3))
        fig.add_vline(x=meses1, line_dash="dot", line_color=STONE)
        fig.update_yaxes(tickprefix="$", tickformat=",.0f")
        style_fig(fig, "¿Cómo cambia el valor final si cambia el plazo?", "Plazo (meses)", "Valor final neto (COP)")
        # Tres nombres largos: la leyenda va debajo para no tapar el título
        fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0),
                          margin=dict(b=40), height=420)
        show_plot(fig)

        mejor = r1["mejor"]
        texto1 = (f"Decisión: {mejor['nombre']} deja {money(mejor['neto'])} de ganancia neta a {meses1} meses, "
                  f"con EA neta de {mejor['ea_neta'] * 100:.2f}%. ")
        for pr in r1["prods"]:
            if pr["neto"] < 0:
                texto1 += (f"{pr['nombre']} pierde {money(-pr['neto'])}: sus intereses no alcanzan a cubrir la "
                           "cuota de manejo. ")
        texto1 += (f"Referencia: si el CDT se liquidara a interés simple con su tasa nominal, el valor final sería "
                   f"{money(r1['vf_simple'])} frente a {money(r1['vf_comp'])} a interés compuesto.")
        callout(texto1, "info")

# ---------------------------------------------------------------------------
# CASO 2
# ---------------------------------------------------------------------------
with tab2:
    col_in, col_out = st.columns([1, 2.4], gap="large")
    with col_in:
        with st.container(border=True):
            section("Datos del caso", "Dos ofertas de crédito para el mismo monto y plazo.")
            fuente2 = st.text_input("Fuente de los datos", key="c2_fuente")
            fecha2 = st.text_input("Fecha de consulta", key="c2_fecha")
            cap2 = st.number_input("Valor del crédito ($)", min_value=1_000.0, step=1_000_000.0, key="c2_cap")
            anios2 = st.number_input("Plazo (años)", min_value=0.25, max_value=40.0, step=0.25, key="c2_anios")
        ofertas = {}
        for clave in ("a", "b"):
            with st.container(border=True):
                nombre = st.text_input("Nombre de la oferta", key=f"c2_{clave}_n")
                tipo = st.selectbox("Tipo de tasa", TIPOS_TASA, key=f"c2_{clave}_t")
                val = st.number_input("Valor de la tasa (%)", min_value=0.0001, max_value=99.0,
                                      step=0.1, format="%.4f", key=f"c2_{clave}_v")
                per = st.selectbox("Periodicidad", list(PERIODICIDADES), key=f"c2_{clave}_p")
                ofertas[clave] = (nombre, tipo, val, per)

    p2 = dict(cap=cap2, anios=anios2, fuente=fuente2, fecha=fecha2,
              a_nombre=ofertas["a"][0], a_tipo=ofertas["a"][1], a_val=ofertas["a"][2], a_per=ofertas["a"][3],
              b_nombre=ofertas["b"][0], b_tipo=ofertas["b"][1], b_val=ofertas["b"][2], b_per=ofertas["b"][3])
    r2 = calcular_caso2(p2)

    with col_out:
        cols = st.columns(2)
        for col, of in zip(cols, (r2["a"], r2["b"])):
            with col:
                kpi(f"{of['nombre']} · EA", pct(of["ea"], 2),
                    f"Cuota: {money(of['cuota'])} · Total: {money(of['total'])}",
                    accent=(of is r2["mejor"]) and not r2["iguales"])
        st.write("")
        tabla = pd.DataFrame({
            "Concepto": ["Tasa efectiva anual", "Tasa periódica", "Número de cuotas", "Primera cuota",
                         "Intereses totales", "Total pagado"],
            **{of["nombre"]: [pct(of["ea"], 4), pct(of["i"], 4), of["n"], money(of["cuota"], 2),
                              money(of["intereses"], 2), money(of["total"], 2)] for of in (r2["a"], r2["b"])},
        })
        tabla = tabla.astype(str)
        show_table(tabla)

        fig = go.Figure()
        for of, color in zip((r2["a"], r2["b"]), (WINE, STONE)):
            t = of["tabla"]
            # El eje va en años para comparar bien ofertas con distinta periodicidad de pago
            fig.add_scatter(x=[0] + (t["Periodo"] / of["m"]).tolist(), y=[cap2] + t["Saldo"].tolist(),
                            name=of["nombre"], mode="lines", line=dict(color=color, width=3))
        fig.update_yaxes(tickprefix="$", tickformat=",.0f")
        style_fig(fig, "Saldo de la deuda en cada oferta", "Años", "Saldo (COP)")
        show_plot(fig)

        fig2 = go.Figure()
        tope = max(10.0, math.ceil(anios2) + 2.0)          # el plazo elegido siempre queda dentro
        paso = 0.5 if tope <= 15 else 1.0
        anios_rango = [paso * k for k in range(1, int(tope / paso) + 1)]
        for of, clave, color in ((r2["a"], "a", WINE), (r2["b"], "b", STONE)):
            _, tipo, val, per = ofertas[clave]
            ys = [_oferta(cap2, a, tipo, val, per)["total"] for a in anios_rango]
            fig2.add_scatter(x=anios_rango, y=ys, name=of["nombre"], mode="lines", line=dict(color=color, width=3))
        fig2.add_vline(x=anios2, line_dash="dot", line_color=STONE)
        fig2.update_yaxes(tickprefix="$", tickformat=",.0f")
        style_fig(fig2, "¿Cómo cambia el total pagado si cambia el plazo?", "Plazo (años)", "Total pagado (COP)")
        show_plot(fig2)

        texto2 = "Decisión: " + decision_caso2(r2) + " "
        if not r2["iguales"]:
            texto2 += ("Se decide por la tasa efectiva anual, no por el total pagado: el total suma pesos de "
                       "fechas distintas. ")
            if r2["dif_total"] < 0:
                texto2 += (f"Aquí {r2['mejor']['nombre']} suma más en cuotas ({money(-r2['dif_total'])}) "
                           "porque paga con menos frecuencia, pero sigue siendo la más barata. ")
        elif abs(r2["dif_total"]) > 0.5:
            texto2 += ("Los totales pagados difieren solo porque cambia la periodicidad de pago, "
                       "no el costo. ")
        variable = [of["nombre"] for of in (r2["a"], r2["b"])
                    if any(x in of["nombre"].lower() for x in ("variable", "ibr", "dtf"))]
        if variable:
            texto2 += (f"Ojo: «{variable[0]}» depende del IBR y el cálculo supone que ese indicador no cambia; "
                       "si sube, la cuota y el costo suben, y la ventaja frente a la tasa fija puede desaparecer. ")
        texto2 += (f"Con abono constante a capital, {r2['mejor']['nombre']} pagaría "
                   f"{money(r2['mejor']['intereses'] - r2['int_abono_constante'])} menos en intereses, pero con "
                   f"una primera cuota de {money(r2['primera_cuota_ac'])}.")
        callout(texto2, "info")

# ---------------------------------------------------------------------------
# CASO 3
# ---------------------------------------------------------------------------
with tab3:
    col_in, col_out = st.columns([1, 2.4], gap="large")
    with col_in:
        with st.container(border=True):
            section("Datos del caso", "Ahorro con cuotas crecientes para una meta.")
            fuente3 = st.text_input("Fuente de los datos", key="c3_fuente")
            fecha3 = st.text_input("Fecha de consulta", key="c3_fecha")
            meta = st.number_input("Meta de ahorro ($)", min_value=1.0, step=1_000_000.0, key="c3_meta")
            meses3 = st.slider("Plazo (meses)", 6, 120, key="c3_meses")
            ea3 = st.number_input("Tasa del ahorro (EA %)", min_value=0.0, step=0.1, key="c3_ea")
            grad = st.radio("Tipo de gradiente", ["Aritmético", "Geométrico"], horizontal=True, key="c3_grad")
            if grad == "Aritmético":
                g_arit = st.number_input("Gradiente (G, $ por mes)", step=1_000.0, key="c3_ga")
                g_geom = st.session_state["c3_gg"]
            else:
                g_geom = st.number_input("Gradiente (g, % por mes)", step=0.1, key="c3_gg")
                g_arit = st.session_state["c3_ga"]

    p3 = dict(meta=meta, meses=meses3, ea=ea3, grad=grad, g_arit=g_arit, g_geom=g_geom, fuente=fuente3, fecha=fecha3)
    r3 = calcular_caso3(p3)

    with col_out:
        if r3["a1"] <= 0:
            callout("Con este gradiente la primera cuota resulta negativa: la meta se alcanza antes de lo previsto. "
                    "Reduce el gradiente.", "warn")
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            kpi("Primera cuota", money(r3["a1"]), f"Uniforme: {money(r3['cuota_unif'])}", accent=True)
        with k2:
            kpi("Última cuota", money(r3["ultima"]))
        with k3:
            kpi("Total aportado", money(r3["total"]), f"Con cuota uniforme: {money(r3['total_unif'])}")
        with k4:
            kpi("Intereses ganados", money(r3["intereses"]), f"Tasa mensual: {pct(r3['i'], 4)}")

        st.write("")
        meses_x = list(range(1, r3["n"] + 1))
        fig = go.Figure()
        fig.add_bar(x=meses_x, y=r3["flujos"], name="Cuota con gradiente", marker_color=BLUSH)
        fig.add_hline(y=r3["cuota_unif"], line_dash="dash", line_color=WINE,
                      annotation_text=f"Cuota uniforme: {money(r3['cuota_unif'])}", annotation_position="top left")
        fig.update_yaxes(tickprefix="$", tickformat=",.0f")
        style_fig(fig, "Plan de aportes mensuales", "Mes", "Aporte (COP)")
        fig.update_layout(hovermode="closest", showlegend=False)
        show_plot(fig)

        tasas = [x / 2 for x in range(0, 31)]
        fig2 = go.Figure()
        fig2.add_scatter(x=tasas, y=[primera_cuota_requerida(p3, x) for x in tasas],
                         name="Primera cuota con gradiente", mode="lines", line=dict(color=WINE, width=3))
        fig2.add_scatter(x=tasas, y=[meta / factor_vf_serie((1 + x / 100) ** (1 / 12) - 1, meses3) for x in tasas],
                         name="Cuota uniforme", mode="lines", line=dict(color=STONE, width=3))
        fig2.add_vline(x=ea3, line_dash="dot", line_color=STONE)
        fig2.update_yaxes(tickprefix="$", tickformat=",.0f")
        style_fig(fig2, "¿Cómo cambia el aporte inicial si cambia la tasa?", "Tasa efectiva anual (%)", "Primera cuota (COP)")
        show_plot(fig2)

        dif3 = r3["cuota_unif"] - r3["a1"]
        if r3["a1"] <= 0:
            texto3 = "Decisión: ajusta el gradiente; con este valor el plan no tiene sentido financiero."
        elif abs(dif3) < 0.005:
            texto3 = (f"Decisión: sin gradiente, aportas {money(r3['a1'])} todos los meses, igual que la cuota "
                      "uniforme.")
        elif dif3 > 0:
            texto3 = (f"Decisión: con gradiente {grad.lower()} empiezas aportando {money(r3['a1'])} al mes, "
                      f"{money(dif3)} menos que con cuota uniforme, y llegas a {money(r3['ultima'])} en el mes "
                      f"{meses3}. Conviene si tu ingreso crece a lo largo del plazo.")
        else:
            texto3 = (f"Decisión: con este gradiente las cuotas bajan: empiezas aportando {money(r3['a1'])} al mes, "
                      f"{money(-dif3)} más que con cuota uniforme, y terminas en {money(r3['ultima'])} en el mes "
                      f"{meses3}. Conviene si esperas que tu ingreso disminuya o quieres adelantar el esfuerzo.")
        callout(texto3, "info")

# ---------------------------------------------------------------------------
# RESUMEN (también alimenta el panel principal)
# ---------------------------------------------------------------------------
guardar_campos()
params = {"c1": p1, "c2": p2, "c3": p3}
st.session_state["casos_params"] = params
resumen = calcular_casos(params)

with tab_res:
    m1, m2 = r1["mejor"], r2["mejor"]
    k1, k2, k3 = st.columns(3)
    with k1:
        kpi(f"Caso 1 · Invertir en {m1['nombre']}", money(m1["vf"]),
            f"Valor final neto a {meses1} meses · EA neta {pct(m1['ea_neta'], 2)}", accent=True)
    with k2:
        if r2["iguales"]:
            kpi("Caso 2 · Las ofertas cuestan igual", pct(m2["ea"], 2), "Misma tasa efectiva anual")
        else:
            kpi(f"Caso 2 · Elegir {m2['nombre']}", money(r2["ahorro_vp"]),
                f"Ahorro en valor presente · EA {pct(m2['ea'], 2)}")
    with k3:
        kpi(f"Caso 3 · Ahorro con gradiente {grad.lower()}", money(r3["a1"]),
            f"Primera cuota para llegar a {money(meta)} en {meses3} meses")

    st.write("")
    section("Resumen de los casos aplicados")
    show_table(resumen)
    st.download_button("Descargar resumen (CSV)", resumen.to_csv(index=False).encode("utf-8"),
                       file_name="resumen_casos.csv", mime="text/csv")

    st.write("")
    section("Temas del curso en cada caso", "Cómo los tres casos, en conjunto, aplican los seis temas.")
    matriz = pd.DataFrame([
        {"Tema": tema,
         "Caso 1": "✅ Sí" if usa[0] else "—",
         "Caso 2": "✅ Sí" if usa[1] else "—",
         "Caso 3": "✅ Sí" if usa[2] else "—",
         "Dónde se ve": donde}
        for tema, usa, donde in TEMAS_POR_CASO
    ])
    show_table(matriz)
    faltan = [tema for tema, usa, _ in TEMAS_POR_CASO if not any(usa)]
    if faltan:
        callout("Falta cubrir: " + ", ".join(faltan) + ".", "warn")
    else:
        callout(f"Los tres casos cubren los {len(TEMAS_POR_CASO)} temas del curso.", "ok")

    st.write("")
    section("Fuentes y fechas de consulta")
    fuentes = pd.DataFrame({
        "Caso": ["1. Inversión", "2. Crédito", "3. Plan de ahorro"],
        "Fuente": [p1["fuente"], p2["fuente"], p3["fuente"]],
        "Fecha de consulta": [p1["fecha"], p2["fecha"], p3["fecha"]],
    })
    show_table(fuentes)
    if any("COMPLETAR" in x or not x.strip()
           for x in fuentes["Fuente"].tolist() + fuentes["Fecha de consulta"].tolist()):
        callout("Hay casos sin fuente o sin fecha de consulta.", "warn")

# ---------------------------------------------------------------------------
# SUPUESTOS Y VERIFICACIÓN
# ---------------------------------------------------------------------------
with tab_ver:
    s1, s2, s3 = st.columns(3)
    with s1:
        with st.container(border=True):
            section("Caso 1 · Inversión")
            st.markdown(
                "- Interés compuesto con la EA de cada producto durante el plazo.\n"
                "- La retención se aplica una sola vez, sobre los intereses al vencimiento.\n"
                "- La cuota de manejo de la cuenta de ahorros se resta de la ganancia, como en el VTUP.\n"
                "- Inflación + puntos se combinan como (1 + π)(1 + p) − 1 y se suponen constantes."
            )
            st.latex(r"EA_{neta}=\left(\frac{VF_{neto}}{C}\right)^{1/t}-1")
    with s2:
        with st.container(border=True):
            section("Caso 2 · Crédito")
            st.markdown(
                "- Cuota fija vencida; el número de cuotas es plazo × pagos por año, redondeado.\n"
                "- Se elige la oferta con menor EA. La diferencia en pesos se mide en valor presente, "
                "con la tasa de la oferta barata.\n"
                "- El total pagado se muestra, pero no decide: suma pesos de fechas distintas.\n"
                "- La tasa variable (IBR + puntos) se supone constante durante todo el plazo."
            )
            st.latex(r"A=P\,\frac{i}{1-(1+i)^{-n}}")
    with s3:
        with st.container(border=True):
            section("Caso 3 · Plan de ahorro")
            st.markdown(
                "- Aportes mensuales al final de cada mes, a la tasa mensual equivalente a la EA.\n"
                "- La primera cuota se despeja para que el valor futuro de todos los aportes sea la meta.\n"
                "- La tasa del ahorro se supone constante."
            )
            st.latex(r"VF=A_1\,s_{n,i}+\frac{G}{i}\left(s_{n,i}-n\right)")

    st.write("")
    section("Verificación contra cálculo manual", "Se comprueban los tres casos con los datos actuales.")
    filas = []
    t1 = meses1 / 12
    for pr in r1["prods"]:
        filas.append((f"Caso 1 · {pr['nombre']}: C(1 + EA neta)^t = valor final neto",
                      cap1 * (1 + pr["ea_neta"]) ** t1, pr["vf"]))
    cdt = r1["prods"][0]
    ah = r1["prods"][1]
    filas += [
        ("Caso 1 · CDT: intereses brutos = C[(1 + EA)^t − 1]", cdt["bruto"], cap1 * ((1 + cdt["ea"]) ** t1 - 1)),
        ("Caso 1 · Cuenta de ahorros: ganancia = intereses − retención − cuota de manejo × meses", ah["neto"],
         ah["bruto"] * (1 - ret1 / 100) - ah_costo * meses1),
        ("Caso 1 · CDT: retención = intereses brutos × tarifa", cdt["retencion"], cdt["bruto"] * ret1 / 100),
        ("Caso 1 · Inflación + puntos = (1 + π)(1 + p) − 1", r1["prods"][2]["ea"],
         (1 + infl1 / 100) * (1 + pts1 / 100) - 1),
    ]
    # Con los datos del simulador de Bancolombia (50 millones, 360 días, 9.40 % EA, retención 4 %),
    # el módulo debe dar exactamente la ganancia y la retención que muestra el banco.
    if (abs(cap1 - 50_000_000) < 0.5 and meses1 == 12 and cdt_tipo == "Efectiva anual (EA)"
            and abs(cdt_val - 9.40) < 1e-9 and abs(ret1 - 4.0) < 1e-9):
        filas += [
            ("Caso 1 · CDT: ganancia neta = simulador de Bancolombia", cdt["neto"], 4_512_000.00),
            ("Caso 1 · CDT: retención = simulador de Bancolombia", cdt["retencion"], 188_000.00),
        ]
    for of in (r2["a"], r2["b"]):
        t = of["tabla"]
        filas += [
            (f"Caso 2 · {of['nombre']}: cuota = P·i/(1 − (1 + i)^−n)", of["cuota"], cuota_fija(cap2, of["i"], of["n"])),
            (f"Caso 2 · {of['nombre']}: saldo final = 0", float(t["Saldo"].iloc[-1]), 0.0, cap2),
            (f"Caso 2 · {of['nombre']}: VP de las cuotas = crédito",
             float(sum(c / (1 + of["i"]) ** k for k, c in zip(t["Periodo"], t["Cuota"]))), cap2),
        ]
    filas += [
        ("Caso 3 · VF de los aportes = meta", vf_flujos(r3["flujos"], r3["i"]), meta),
        ("Caso 3 · cuota uniforme × s(n, i) = meta", r3["cuota_unif"] * factor_vf_serie(r3["i"], r3["n"]), meta),
    ]
    if r3["i"] > 0:
        g3 = g_arit if grad == "Aritmético" else g_geom / 100
        filas.append((f"Caso 3 · VF del gradiente {grad.lower()} por fórmula = meta",
                      vf_gradiente_formula(r3["a1"], g3, r3["n"], r3["i"], grad), meta))
    verification_table(filas, tol=1e-6)
