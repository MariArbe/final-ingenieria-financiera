import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.casos import (
    DEFAULTS, _oferta, calcular_caso1, calcular_caso2, calcular_caso3, calcular_casos, primera_cuota_requerida,
)
from utils.financial_math import TIPOS_TASA, PERIODICIDADES, factor_vf_serie
from utils.ui import (
    setup_page, page_header, section, kpi, callout, style_fig,
    show_plot, show_table, money, pct, STONE, WINE, BLUSH,
)

setup_page("Casos aplicados", "🧭")
page_header(
    "Casos aplicados",
    "Tres casos con productos financieros: invertir, endeudarse y ahorrar para una meta. "
    "Cambia los datos y mira cómo cambia la decisión.",
)

d1, d2, d3 = DEFAULTS["c1"], DEFAULTS["c2"], DEFAULTS["c3"]
PALETA = [WINE, STONE, BLUSH]

tab1, tab2, tab3, tab_res = st.tabs([
    "Caso 1 · CDT vs. ahorros", "Caso 2 · Crédito", "Caso 3 · Plan de ahorro", "Resumen",
])

# ---------------------------------------------------------------------------
# CASO 1
# ---------------------------------------------------------------------------
with tab1:
    col_in, col_out = st.columns([1, 2.4], gap="large")
    with col_in:
        with st.container(border=True):
            section("Datos del caso", "Usa ofertas publicadas y anota la fuente.")
            fuente1 = st.text_input("Fuente de los datos", d1["fuente"], key="c1_fuente")
            fecha1 = st.text_input("Fecha de consulta", d1["fecha"], key="c1_fecha")
            cap1 = st.number_input("Capital a invertir ($)", min_value=1.0, value=d1["cap"], step=500_000.0, key="c1_cap")
            meses1 = st.slider("Plazo (meses)", 1, 60, d1["meses"], key="c1_meses")
            ret1 = st.number_input("Retención en la fuente (%)", min_value=0.0, max_value=100.0, value=d1["ret"],
                                   step=0.5, key="c1_ret", help="Confirma la tarifa vigente.")
        with st.container(border=True):
            section("CDT")
            cdt_tipo = st.selectbox("Tipo de tasa", TIPOS_TASA, index=TIPOS_TASA.index(d1["cdt_tipo"]), key="c1_ct")
            cdt_val = st.number_input("Valor de la tasa (%)", min_value=0.0001, max_value=99.0, value=d1["cdt_val"],
                                      step=0.1, format="%.4f", key="c1_cv")
            cdt_per = st.selectbox("Periodicidad", list(PERIODICIDADES), key="c1_cp")
        with st.container(border=True):
            section("Otras alternativas")
            ah_ea = st.number_input("Cuenta de ahorros (EA %)", min_value=0.0, value=d1["ah_ea"], step=0.1, key="c1_ah")
            infl1 = st.number_input("Inflación esperada (EA %)", min_value=0.0, value=d1["infl"], step=0.1, key="c1_inf")
            pts1 = st.number_input("Puntos adicionales (EA %)", min_value=0.0, value=d1["pts"], step=0.1, key="c1_pts")

    p1 = dict(cap=cap1, meses=meses1, cdt_tipo=cdt_tipo, cdt_val=cdt_val, cdt_per=cdt_per, ah_ea=ah_ea,
              ret=ret1, infl=infl1, pts=pts1, fuente=fuente1, fecha=fecha1)
    r1 = calcular_caso1(p1)

    with col_out:
        cols = st.columns(3)
        for col, pr in zip(cols, r1["prods"]):
            with col:
                kpi(pr["nombre"], pct(pr["ea_neta"], 2), f"EA neta · bruta {pct(pr['ea'], 2)}",
                    accent=pr is r1["mejor"])
        st.write("")
        tabla = pd.DataFrame({
            "Concepto": ["Intereses brutos", "Retención", "Intereses netos", "Valor final"],
            **{pr["nombre"]: [money(pr["bruto"]), money(pr["retencion"]), money(pr["neto"]), money(pr["vf"])]
               for pr in r1["prods"]},
        })
        show_table(tabla)

        fig = go.Figure()
        for pr, color in zip(r1["prods"], PALETA):
            xs = list(range(1, 61))
            ys = [cap1 + (cap1 * ((1 + pr["ea"]) ** (mm / 12) - 1)) * (1 - ret1 / 100) for mm in xs]
            fig.add_scatter(x=xs, y=ys, name=pr["nombre"], mode="lines", line=dict(color=color, width=3))
        fig.add_vline(x=meses1, line_dash="dot", line_color=STONE)
        fig.update_yaxes(tickprefix="$", tickformat=",.0f")
        style_fig(fig, "¿Cómo cambia el valor final si cambia el plazo?", "Plazo (meses)", "Valor final neto (COP)")
        show_plot(fig)

        mejor = r1["mejor"]
        callout(
            f"Decisión: {mejor['nombre']} deja {money(mejor['neto'])} en intereses netos a {meses1} meses, "
            f"con EA neta de {mejor['ea_neta'] * 100:.2f}%. "
            f"Referencia: si el CDT se liquidara a interés simple con su tasa nominal, el valor final sería "
            f"{money(r1['vf_simple'])} frente a {money(r1['vf_comp'])} a interés compuesto.",
            "info",
        )

# ---------------------------------------------------------------------------
# CASO 2
# ---------------------------------------------------------------------------
with tab2:
    col_in, col_out = st.columns([1, 2.4], gap="large")
    with col_in:
        with st.container(border=True):
            section("Datos del caso", "Dos ofertas de crédito para el mismo monto y plazo.")
            fuente2 = st.text_input("Fuente de los datos", d2["fuente"], key="c2_fuente")
            fecha2 = st.text_input("Fecha de consulta", d2["fecha"], key="c2_fecha")
            cap2 = st.number_input("Valor del crédito ($)", min_value=1_000.0, value=d2["cap"], step=1_000_000.0, key="c2_cap")
            anios2 = st.number_input("Plazo (años)", min_value=0.25, max_value=40.0, value=d2["anios"], step=0.25, key="c2_anios")
        ofertas = {}
        for clave, d in (("a", d2), ("b", d2)):
            with st.container(border=True):
                nombre = st.text_input("Nombre de la oferta", d[f"{clave}_nombre"], key=f"c2_{clave}_n")
                tipo = st.selectbox("Tipo de tasa", TIPOS_TASA, index=TIPOS_TASA.index(d[f"{clave}_tipo"]), key=f"c2_{clave}_t")
                val = st.number_input("Valor de la tasa (%)", min_value=0.0001, max_value=99.0, value=d[f"{clave}_val"],
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
                    f"Cuota: {money(of['cuota'])} · Total: {money(of['total'])}", accent=of is r2["mejor"])
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
            fig.add_scatter(x=[0] + t["Periodo"].tolist(), y=[cap2] + t["Saldo"].tolist(),
                            name=of["nombre"], mode="lines", line=dict(color=color, width=3))
        fig.update_yaxes(tickprefix="$", tickformat=",.0f")
        style_fig(fig, "Saldo de la deuda en cada oferta", "Periodo", "Saldo (COP)")
        show_plot(fig)

        fig2 = go.Figure()
        anios_rango = [a / 2 for a in range(2, 21)]
        for clave, color in (("a", WINE), ("b", STONE)):
            nombre, tipo, val, per = ofertas[clave]
            ys = [_oferta(cap2, a, tipo, val, per)["total"] for a in anios_rango]
            fig2.add_scatter(x=anios_rango, y=ys, name=nombre, mode="lines", line=dict(color=color, width=3))
        fig2.add_vline(x=anios2, line_dash="dot", line_color=STONE)
        fig2.update_yaxes(tickprefix="$", tickformat=",.0f")
        style_fig(fig2, "¿Cómo cambia el total pagado si cambia el plazo?", "Plazo (años)", "Total pagado (COP)")
        show_plot(fig2)

        callout(
            f"Decisión: {r2['mejor']['nombre']} es más económica; paga {money(r2['ahorro'])} menos en total que "
            f"{r2['peor']['nombre']}. Con abono constante a capital, esa misma oferta pagaría "
            f"{money(r2['mejor']['intereses'] - r2['int_abono_constante'])} menos en intereses, pero con una "
            f"primera cuota de {money(r2['primera_cuota_ac'])}.",
            "info",
        )

# ---------------------------------------------------------------------------
# CASO 3
# ---------------------------------------------------------------------------
with tab3:
    col_in, col_out = st.columns([1, 2.4], gap="large")
    with col_in:
        with st.container(border=True):
            section("Datos del caso", "Ahorro con cuotas crecientes para una meta.")
            fuente3 = st.text_input("Fuente de los datos", d3["fuente"], key="c3_fuente")
            fecha3 = st.text_input("Fecha de consulta", d3["fecha"], key="c3_fecha")
            meta = st.number_input("Meta de ahorro ($)", min_value=1.0, value=d3["meta"], step=1_000_000.0, key="c3_meta")
            meses3 = st.slider("Plazo (meses)", 6, 120, d3["meses"], key="c3_meses")
            ea3 = st.number_input("Tasa del ahorro (EA %)", min_value=0.0, value=d3["ea"], step=0.1, key="c3_ea")
            grad = st.radio("Tipo de gradiente", ["Aritmético", "Geométrico"], horizontal=True, key="c3_grad")
            if grad == "Aritmético":
                g_arit = st.number_input("Gradiente (G, $ por mes)", value=d3["g_arit"], step=1_000.0, key="c3_ga")
                g_geom = d3["g_geom"]
            else:
                g_geom = st.number_input("Gradiente (g, % por mes)", value=d3["g_geom"], step=0.1, key="c3_gg")
                g_arit = d3["g_arit"]

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

        callout(
            f"Decisión: con gradiente {grad.lower()} empiezas aportando {money(r3['a1'])} al mes, "
            f"{money(r3['cuota_unif'] - r3['a1'])} menos que con cuota uniforme, y llegas a {money(r3['ultima'])} "
            f"en el mes {meses3}. Conviene si tu ingreso crece a lo largo del plazo.",
            "info",
        )

# ---------------------------------------------------------------------------
# RESUMEN (también alimenta el panel principal)
# ---------------------------------------------------------------------------
params = {"c1": p1, "c2": p2, "c3": p3}
st.session_state["casos_params"] = params

with tab_res:
    section("Resumen de los casos aplicados", "Es la misma tabla que aparece en el panel principal.")
    show_table(calcular_casos(params))
    st.write("")
    section("Fuentes y fechas de consulta")
    fuentes = pd.DataFrame({
        "Caso": ["1. Inversión", "2. Crédito", "3. Plan de ahorro"],
        "Fuente": [p1["fuente"], p2["fuente"], p3["fuente"]],
        "Fecha de consulta": [p1["fecha"], p2["fecha"], p3["fecha"]],
    })
    show_table(fuentes)
    if any("COMPLETAR" in x for x in fuentes["Fuente"].tolist() + fuentes["Fecha de consulta"].tolist()):
        callout("Faltan fuentes o fechas: la rúbrica las exige en cada caso. Complétalas en la parte superior de cada pestaña.", "warn")