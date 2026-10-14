import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.financial_math import (
    TIPOS_TASA, TASA_EA, PERIODICIDADES,
    a_efectiva_anual, desde_efectiva_anual, anticipada_a_vencida,
    tasa_combinada, inflacion_de_equilibrio, ea_neta,
)
from utils.ui import (
    setup_page, page_header, section, kpi, callout, style_fig,
    show_plot, show_table, verification_table, money, pct, STONE, WINE, BLUSH,
)

setup_page("Rentabilidad y tasas", "💱")
page_header(
    "Rentabilidad y equivalencia de tasas",
    "Convierte entre tasas periódicas, nominales y efectivas, vencidas y anticipadas; combina inflación "
    "con puntos adicionales y calcula la rentabilidad neta después de la retención en la fuente.",
)

tab_conv, tab_comb, tab_ret, tab_ver = st.tabs([
    "Convertidor y equivalencias", "Tasa combinada", "Retención en la fuente", "Supuestos y verificación",
])

# ---------------------------------------------------------------------------
# 1) CONVERTIDOR Y TABLA DE EQUIVALENCIAS
# ---------------------------------------------------------------------------
with tab_conv:
    col_in, col_out = st.columns([1, 2.4], gap="large")
    with col_in:
        with st.container(border=True):
            section("Tasa de entrada", "La tabla de equivalencias se recalcula al cambiar la tasa.")
            tipo = st.selectbox("Tipo de tasa", TIPOS_TASA)
            valor_pct = st.number_input("Valor de la tasa (%)", min_value=0.0001, max_value=99.0,
                                        value=12.0, step=0.1, format="%.4f")
            per_nombre = st.selectbox("Periodicidad", list(PERIODICIDADES),
                                      help="Aplica a tasas nominales y periódicas, y a los resultados que se muestran arriba.")
            m = PERIODICIDADES[per_nombre]

    ea_in = a_efectiva_anual(tipo, valor_pct / 100, m)
    eq = desde_efectiva_anual(ea_in, m)

    with col_out:
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            kpi("Efectiva anual", pct(ea_in), "EA equivalente", accent=True)
        with k2:
            kpi(f"Periódica vencida", pct(eq["periodica_vencida"]), per_nombre.lower())
        with k3:
            kpi("Nominal vencida", pct(eq["nominal_vencida"]), f"capitalización {per_nombre.lower()}")
        with k4:
            kpi("Periódica anticipada", pct(eq["periodica_anticipada"]), per_nombre.lower())

        st.write("")
        filas = []
        for nombre, mm in PERIODICIDADES.items():
            e = desde_efectiva_anual(ea_in, mm)
            filas.append({
                "Periodicidad": nombre,
                "Periodos por año": mm,
                "Periódica vencida": pct(e["periodica_vencida"]),
                "Nominal vencida": pct(e["nominal_vencida"]),
                "Periódica anticipada": pct(e["periodica_anticipada"]),
                "Nominal anticipada": pct(e["nominal_anticipada"]),
                "EA": pct(ea_in),
            })
        section("Tabla de equivalencias")
        show_table(pd.DataFrame(filas))

        nominales = [desde_efectiva_anual(ea_in, mm)["nominal_vencida"] * 100 for mm in PERIODICIDADES.values()]
        fig = go.Figure()
        fig.add_bar(x=list(PERIODICIDADES), y=nominales, name="Nominal vencida",
                    marker_color=BLUSH, hovertemplate="%{y:.4f}%<extra></extra>")
        fig.add_hline(y=ea_in * 100, line_dash="dash", line_color=WINE,
                      annotation_text=f"EA = {ea_in * 100:.4f}%", annotation_position="top left")
        fig.update_yaxes(ticksuffix="%", rangemode="tozero")
        style_fig(fig, "Tasa nominal vencida equivalente según periodicidad",
                  "Periodicidad de capitalización", "Tasa nominal anual (%)")
        fig.update_layout(showlegend=False, height=320)
        show_plot(fig)

# ---------------------------------------------------------------------------
# 2) TASA COMBINADA
# ---------------------------------------------------------------------------
with tab_comb:
    col_in, col_out = st.columns([1, 2.4], gap="large")
    with col_in:
        with st.container(border=True):
            section("Inversión indexada a inflación", "Inflación + puntos adicionales vs. una tasa fija.")
            cap_c = st.number_input("Capital ($)", min_value=1.0, value=10_000_000.0, step=500_000.0, key="cb_cap")
            infl_pct = st.number_input("Inflación esperada (EA %)", min_value=0.0, value=5.5, step=0.1, key="cb_inf")
            pts_pct = st.number_input("Puntos adicionales (EA %)", min_value=0.0, value=4.0, step=0.1, key="cb_pts")
            fija_pct = st.number_input("Alternativa a tasa fija (EA %)", min_value=0.0, value=10.5, step=0.1, key="cb_fija")
            anios_c = st.slider("Plazo (años)", 1, 15, 5, key="cb_anios")

    infl, pts, fija = infl_pct / 100, pts_pct / 100, fija_pct / 100
    ea_comb = tasa_combinada(infl, pts)
    suma = infl + pts
    infl_eq = inflacion_de_equilibrio(fija, pts)
    vf_comb = cap_c * (1 + ea_comb) ** anios_c
    vf_fija = cap_c * (1 + fija) ** anios_c

    with col_out:
        k1, k2, k3 = st.columns(3)
        with k1:
            kpi("EA combinada", pct(ea_comb, 4), f"Suma simple: {suma * 100:.4f}%", accent=True)
        with k2:
            kpi("EA tasa fija", pct(fija, 4), "alternativa")
        with k3:
            kpi("Inflación de equilibrio", pct(infl_eq, 4), "ambas rinden igual")

        st.write("")
        anios = list(range(anios_c + 1))
        fig = go.Figure()
        fig.add_scatter(x=anios, y=[cap_c * (1 + ea_comb) ** a for a in anios],
                        name="Inflación + puntos", mode="lines+markers", line=dict(color=WINE, width=3))
        fig.add_scatter(x=anios, y=[cap_c * (1 + fija) ** a for a in anios],
                        name="Tasa fija", mode="lines+markers", line=dict(color=STONE, width=3))
        fig.update_yaxes(tickprefix="$", tickformat=",.0f")
        style_fig(fig, "Valor acumulado de cada alternativa", "Tiempo (años)", "Valor acumulado (COP)")
        show_plot(fig)

        mejor = "inflación + puntos" if vf_comb > vf_fija else "tasa fija"
        callout(
            f"Al cabo de {anios_c} años, la opción de {mejor} deja {money(abs(vf_comb - vf_fija))} más. "
            f"La inversión indexada gana mientras la inflación promedio supere {infl_eq * 100:.2f}%.",
            "info",
        )

# ---------------------------------------------------------------------------
# 3) RETENCIÓN EN LA FUENTE
# ---------------------------------------------------------------------------
with tab_ret:
    col_in, col_out = st.columns([1, 2.4], gap="large")
    with col_in:
        with st.container(border=True):
            section("Condiciones comunes")
            cap_r = st.number_input("Capital ($)", min_value=1.0, value=20_000_000.0, step=500_000.0, key="rt_cap")
            meses = st.slider("Plazo (meses)", 1, 60, 12, key="rt_meses")
        with st.container(border=True):
            section("Producto A")
            nombre_a = st.text_input("Nombre", value="CDT", key="rt_na")
            ea_a = st.number_input("Tasa EA bruta (%)", min_value=0.0, value=10.0, step=0.1, key="rt_ea_a")
            ret_a = st.number_input("Retención en la fuente (%)", min_value=0.0, max_value=100.0, value=4.0,
                                    step=0.5, key="rt_ret_a",
                                    help="Confirma la tarifa vigente antes de la entrega.")
        with st.container(border=True):
            section("Producto B")
            nombre_b = st.text_input("Nombre", value="Cuenta de ahorros", key="rt_nb")
            ea_b = st.number_input("Tasa EA bruta (%)", min_value=0.0, value=8.0, step=0.1, key="rt_ea_b")
            ret_b = st.number_input("Retención en la fuente (%)", min_value=0.0, max_value=100.0, value=4.0,
                                    step=0.5, key="rt_ret_b")

    t = meses / 12

    def resultado(ea, ret):
        ea, ret = ea / 100, ret / 100
        bruto = cap_r * ((1 + ea) ** t - 1)
        retencion = bruto * ret
        return {
            "ea": ea, "ea_neta": ea_neta(ea, ret, t), "bruto": bruto,
            "retencion": retencion, "neto": bruto - retencion, "vf": cap_r + bruto - retencion,
        }

    ra, rb = resultado(ea_a, ret_a), resultado(ea_b, ret_b)

    with col_out:
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            kpi(f"EA neta · {nombre_a}", pct(ra["ea_neta"]), f"Bruta: {pct(ra['ea'])}", accent=True)
        with k2:
            kpi(f"Intereses netos · {nombre_a}", money(ra["neto"]), f"Retención: {money(ra['retencion'])}")
        with k3:
            kpi(f"EA neta · {nombre_b}", pct(rb["ea_neta"]), f"Bruta: {pct(rb['ea'])}", accent=True)
        with k4:
            kpi(f"Intereses netos · {nombre_b}", money(rb["neto"]), f"Retención: {money(rb['retencion'])}")

        st.write("")
        fig = go.Figure()
        fig.add_bar(x=[nombre_a, nombre_b], y=[ra["ea"] * 100, rb["ea"] * 100], name="EA bruta",
                    marker_color=BLUSH, hovertemplate="%{y:.4f}%<extra></extra>")
        fig.add_bar(x=[nombre_a, nombre_b], y=[ra["ea_neta"] * 100, rb["ea_neta"] * 100], name="EA neta",
                    marker_color=WINE, hovertemplate="%{y:.4f}%<extra></extra>")
        fig.update_layout(barmode="group", hovermode="closest")
        fig.update_yaxes(ticksuffix="%", rangemode="tozero")
        style_fig(fig, "Rentabilidad efectiva anual: bruta vs. neta", "Producto", "Tasa efectiva anual (%)")
        fig.update_layout(hovermode="closest")
        show_plot(fig)

        tabla = pd.DataFrame({
            "Concepto": ["Intereses brutos", "Retención en la fuente", "Intereses netos", "Valor final neto"],
            nombre_a: [money(ra["bruto"], 2), money(ra["retencion"], 2), money(ra["neto"], 2), money(ra["vf"], 2)],
            nombre_b: [money(rb["bruto"], 2), money(rb["retencion"], 2), money(rb["neto"], 2), money(rb["vf"], 2)],
        })
        show_table(tabla)

        ganador, perdedor = (nombre_a, nombre_b) if ra["neto"] >= rb["neto"] else (nombre_b, nombre_a)
        dif = abs(ra["neto"] - rb["neto"])
        callout(f"Después de retención, {ganador} entrega {money(dif)} más en intereses que {perdedor} "
                f"a {meses} meses.", "info")

# ---------------------------------------------------------------------------
# 4) SUPUESTOS Y VERIFICACIÓN
# ---------------------------------------------------------------------------
with tab_ver:
    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        with st.container(border=True):
            section("Supuestos")
            st.markdown(
                "- **Base de tiempo:** año de 12 periodos; la EA es la tasa de referencia.\n"
                "- **Tasas vencidas:** los intereses se pagan al final del periodo.\n"
                "- **Tasas anticipadas:** los intereses se pagan al inicio del periodo.\n"
                "- **Retención:** se aplica sobre los intereses brutos al vencimiento.\n"
                "- **Tarifa de retención:** es un parámetro; confírmala con la fuente de cada caso."
            )
    with col_b:
        with st.container(border=True):
            section("Fórmulas empleadas")
            st.latex(r"EA=\left(1+\frac{j}{m}\right)^m-1\qquad i_a=\frac{i_v}{1+i_v}\qquad i_v=\frac{i_a}{1-i_a}")
            st.latex(r"EA_{comb}=(1+\pi)(1+r)-1")
            st.latex(r"EA_{neta}=\left[1+\left((1+EA)^t-1\right)(1-ret)\right]^{1/t}-1")

    st.write("")
    section("Verificación contra cálculo manual", "Se usan los valores actuales de las otras pestañas.")
    iv = eq["periodica_vencida"]
    ia = eq["periodica_anticipada"]
    filas = [
        ("EA → periódica → EA", (1 + iv) ** m - 1, ea_in),
        ("Anticipada → vencida (i_a/(1−i_a))", ia / (1 - ia), iv),
        ("Nominal capitalizada m veces rinde la EA", (1 + eq["nominal_vencida"] / m) ** m - 1, ea_in),
        ("Tasa combinada (1+π)(1+r)−1", ea_comb, (1 + infl) * (1 + pts) - 1),
        ("Fisher: (1+EA comb)/(1+π)−1 = puntos", (1 + ea_comb) / (1 + infl) - 1, pts),
        ("EA neta: (1+EA_neta)^t = 1+intereses netos/C", (1 + ra["ea_neta"]) ** t, 1 + ra["neto"] / cap_r),
    ]
    verification_table(filas)