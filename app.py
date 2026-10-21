import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.casos import DEFAULTS, calcular_casos
from utils.resumen import (
    resumen_interes, resumen_tasas, resumen_series, resumen_amortizacion, resumen_casos,
    TEMAS_CURSO, TEMAS_POR_MODULO,
)
from utils.ui import (
    setup_page, page_header, section, kpi, callout, safe_page_link, show_table, show_plot, style_fig,
    resumen_modulo, mini_fig, money, pct, BLUSH, WINE, STONE,
)
from utils.verificacion import verificar_todo

setup_page("Tablero de Ingeniería Financiera", "💎")
page_header(
    "Tablero de síntesis y visualización financiera",
    "Interés, rentabilidad, series uniformes, gradientes y amortización, aplicados a productos "
    "e inversiones financieras reales.",
)

# Los casos usan los datos de la página Casos aplicados si ya se abrió; si no, las ofertas consultadas.
params = st.session_state.get("casos_params", DEFAULTS)

# ---------------------------------------------------------------------------
# RESUMEN POR MÓDULO: el resultado clave de cada página con sus valores iniciales
# ---------------------------------------------------------------------------
section("Resumen por módulo",
        "El resultado clave de cada módulo con sus valores iniciales. Abre el módulo para cambiar los datos.")

ri, rt, rs, ra = resumen_interes(), resumen_tasas(), resumen_series(), resumen_amortizacion()
rc = resumen_casos(params)
ei, et, es, ea = ri["ej"], rt["ej"], rs["ej"], ra["ej"]

fila1 = st.columns(3, gap="medium")
with fila1[0]:
    with st.container(border=True, key="modcard_1"):
        resumen_modulo(
            "📈", "Interés simple y compuesto", money(ri["ventaja"]), "más intereses con interés compuesto",
            f"{money(ei['capital'])} al {ei['tasa'] * 100:.1f} % mensual durante {ei['n']} meses: "
            f"{money(ri['vf_comp'])} compuesto frente a {money(ri['vf_simple'])} simple "
            f"({ri['extra_pct'] * 100:.1f} % más intereses).",
        )
        fig = go.Figure()
        fig.add_scatter(x=ri["periodos"], y=ri["simple"], name="Simple", mode="lines",
                        line=dict(color=STONE, width=2.5))
        fig.add_scatter(x=ri["periodos"], y=ri["comp"], name="Compuesto", mode="lines",
                        line=dict(color=WINE, width=2.5))
        fig.update_yaxes(tickprefix="$", tickformat="~s")
        mini_fig(fig)
        safe_page_link("pages/1_Interes_Simple_y_Compuesto.py", label="Abrir módulo")

with fila1[1]:
    with st.container(border=True, key="modcard_2"):
        resumen_modulo(
            "💱", "Rentabilidad y tasas", pct(rt["nominal_mensual"], 2),
            f"nominal mes vencido equivalente a {et['ea'] * 100:.0f} % EA",
            f"Con retención del {et['ret'] * 100:.0f} %, una inversión al {et['ea_ret'] * 100:.0f} % EA rinde "
            f"{pct(rt['ea_neta'], 2)} neto. A más capitalizaciones al año, menor nominal para la misma EA.",
        )
        fig = go.Figure()
        cortos = {"Mensual": "Mes", "Bimestral": "Bim", "Trimestral": "Trim", "Cuatrimestral": "Cuat",
                  "Semestral": "Sem", "Anual": "Año"}
        fig.add_bar(x=[cortos.get(n, n) for n, _ in rt["nominales"]], y=[v * 100 for _, v in rt["nominales"]],
                    marker_color=BLUSH, name="Nominal vencida", text=[f"{v * 100:.2f}" for _, v in rt["nominales"]],
                    textposition="outside", textfont=dict(size=9.5), cliponaxis=False,
                    hovertemplate="%{x}: %{y:.2f}%<extra></extra>")
        fig.update_yaxes(ticksuffix="%", rangemode="tozero")
        mini_fig(fig, etiquetas_x=True)
        safe_page_link("pages/2_Rentabilidad_y_Tasas.py", label="Abrir módulo")

with fila1[2]:
    with st.container(border=True, key="modcard_3"):
        resumen_modulo(
            "🔁", "Series y gradientes", money(rs["vp"]),
            f"valor presente de {es['n']} cuotas de {money(es['cuota'])}",
            f"Al {es['i'] * 100:.1f} % mensual. Un gradiente que empieza en {money(es['a1'])} y sube "
            f"{money(es['g'])} por mes equivale a una cuota fija de {money(rs['cuota_eq'])}.",
        )
        fig = go.Figure()
        fig.add_bar(x=list(range(1, es["ng"] + 1)), y=rs["flujos"], marker_color=BLUSH, name="Cuota",
                    hovertemplate="Mes %{x}: $%{y:,.0f}<extra></extra>")
        fig.add_hline(y=rs["cuota_eq"], line_dash="dash", line_color=WINE, line_width=1.5)
        fig.update_yaxes(tickprefix="$", tickformat="~s")
        mini_fig(fig)
        safe_page_link("pages/3_Series_y_Gradientes.py", label="Abrir módulo")

fila2 = st.columns(2, gap="medium")
with fila2[0]:
    with st.container(border=True, key="modcard_4"):
        resumen_modulo(
            "🧾", "Tablas de amortización", money(ra["cuota"]),
            f"cuota fija de un crédito de {money(ea['capital'])}",
            f"Al {ea['tasa_nmv'] * 100:.0f} % nominal mes vencido a {ea['anios']} años. Con abono constante a "
            f"capital se pagan {money(ra['intereses_cf'] - ra['intereses_ac'])} menos de intereses, pero la "
            f"primera cuota sube a {money(ra['primera_ac'])}.",
        )
        fig = go.Figure()
        fig.add_scatter(x=ra["periodos"], y=ra["saldo_cf"], name="Cuota fija", mode="lines",
                        line=dict(color=WINE, width=2.5))
        fig.add_scatter(x=ra["periodos"], y=ra["saldo_ac"], name="Abono constante", mode="lines",
                        line=dict(color=STONE, width=2.5))
        fig.update_yaxes(tickprefix="$", tickformat="~s")
        mini_fig(fig)
        safe_page_link("pages/4_Tablas_de_Amortizacion.py", label="Abrir módulo")

with fila2[1]:
    with st.container(border=True, key="modcard_5"):
        r1, r2, r3 = rc["r1"], rc["r2"], rc["r3"]
        m1, m2 = r1["mejor"], r2["mejor"]
        credito = (f"las dos opciones de crédito cuestan igual ({pct(m2['ea'], 2)} EA)" if r2["iguales"] else
                   f"en el crédito conviene {m2['nombre']} (ahorra {money(r2['ahorro_vp'])} en valor presente)")
        resumen_modulo(
            "🧭", "Casos aplicados", pct(m1["ea_neta"], 2), f"EA neta de la mejor inversión: {m1['nombre']}",
            f"Con ofertas reales: {credito}, y el plan de ahorro arranca con {money(r3['a1'])} al mes.",
        )
        fig = go.Figure()
        prods = r1["prods"]
        cortos = {"CDT Bancolombia": "CDT", "Cuenta de ahorros Davivienda": "Cuenta de ahorros",
                  "Inversión inflación + puntos": "Inflación + puntos"}
        fig.add_bar(x=[cortos.get(p["nombre"], p["nombre"]) for p in prods], y=[p["neto"] for p in prods],
                    marker_color=[WINE if p is m1 else BLUSH for p in prods], name="Ganancia neta",
                    text=[money(p["neto"]) for p in prods], textposition="outside", textfont=dict(size=9.5),
                    cliponaxis=False, hovertemplate="%{x}: $%{y:,.0f}<extra></extra>")
        fig.update_yaxes(tickprefix="$", tickformat="~s",
                         range=[min(0, min(p["neto"] for p in prods)) * 1.6 - max(p["neto"] for p in prods) * 0.08,
                                max(p["neto"] for p in prods) * 1.25])
        mini_fig(fig, etiquetas_x=True)
        safe_page_link("pages/5_Casos_Aplicados.py", label="Abrir módulo")

st.caption("Gráficos: interés simple (claro) y compuesto (oscuro) en el tiempo · tasa nominal equivalente según "
           "la periodicidad · cuotas del gradiente frente a la cuota fija (línea punteada) · saldo del crédito con "
           "cuota fija (oscuro) y abono constante (claro) · ganancia neta de cada inversión del caso 1.")

# ---------------------------------------------------------------------------
# TEMAS DEL CURSO EN CADA MÓDULO
# ---------------------------------------------------------------------------
st.write("")
section("Temas del curso en cada módulo", "Qué temas trabaja cada módulo y qué se calcula en él.")
show_table(pd.DataFrame([
    {"Módulo": modulo, "Temas del curso": ", ".join(temas), "Qué se calcula": que}
    for modulo, temas, que in TEMAS_POR_MODULO
]))
# Cada tema debe tener un módulo propio (sin contar Casos aplicados, que los reúne todos)
sin_modulo = [t for t in TEMAS_CURSO
              if not any(t in temas for modulo, temas, _ in TEMAS_POR_MODULO if modulo != "Casos aplicados")]
if sin_modulo:
    callout("Temas sin módulo: " + ", ".join(sin_modulo) + ".", "warn")
else:
    callout(f"Los {len(TEMAS_CURSO)} temas del curso tienen su propio módulo y, además, se aplican juntos en "
            "los casos aplicados.", "ok")

st.write("")
col_ver, col_graf = st.columns([1, 1.65], gap="medium")

# ---------------------------------------------------------------------------
# VERIFICACIÓN GLOBAL
# ---------------------------------------------------------------------------
with col_ver:
    verif = verificar_todo(params)
    total = sum(v["Pruebas"] for v in verif)
    ok = sum(v["Coinciden"] for v in verif)
    kpi("Verificaciones que coinciden", f"{ok} de {total}",
        "Cálculo del tablero frente al cálculo manual, en los cinco módulos", accent=True)
    st.write("")
    show_table(pd.DataFrame([
        {"Módulo": v["Módulo"], "Pruebas": v["Pruebas"],
         "Estado": "✅ Coincide" if not v["fallas"] else f"❌ Revisar ({len(v['fallas'])})"}
        for v in verif
    ]))
    fallas = [f"{v['Módulo']}: {f}" for v in verif for f in v["fallas"]]
    if fallas:
        callout("No coinciden: " + "; ".join(fallas[:5]) + ("…" if len(fallas) > 5 else ""), "warn")

# ---------------------------------------------------------------------------
# TASAS DEL MERCADO CONSULTADO (ofertas reales de los casos)
# ---------------------------------------------------------------------------
with col_graf:
    r1, r2 = rc["r1"], rc["r2"]
    ahorros = r1["prods"][1]
    ofertas = [
        (ahorros["nombre"], ahorros["ea"], "Ahorro e inversión"),
        ("Cajitas de ahorro Nu", params["c3"]["ea"] / 100, "Ahorro e inversión"),
        (r1["prods"][0]["nombre"], r1["prods"][0]["ea"], "Ahorro e inversión"),
        (f"Crédito · {r2['a']['nombre']}", r2["a"]["ea"], "Crédito"),
        (f"Crédito · {r2['b']['nombre']}", r2["b"]["ea"], "Crédito"),
    ]
    ofertas.sort(key=lambda o: o[1])
    fig = go.Figure()
    for grupo, color in (("Ahorro e inversión", BLUSH), ("Crédito", WINE)):
        filas = [o for o in ofertas if o[2] == grupo]
        fig.add_bar(y=[o[0] for o in filas], x=[o[1] * 100 for o in filas], orientation="h", name=grupo,
                    marker_color=color, text=[f"{o[1] * 100:.2f}%" for o in filas], textposition="outside",
                    cliponaxis=False, hovertemplate="%{y}: %{x:.2f}% EA<extra></extra>")
    style_fig(fig, "Tasas del mercado consultado", "Tasa efectiva anual (%)", "")
    fig.update_yaxes(categoryorder="array", categoryarray=[o[0] for o in ofertas], showgrid=False)
    fig.update_xaxes(ticksuffix="%", range=[0, max(o[1] for o in ofertas) * 100 * 1.28], showgrid=True,
                     gridcolor="#F6E4EC")
    # Leyenda debajo del eje para que no choque con el título ni se corte
    fig.update_layout(hovermode="closest", height=410, bargap=0.35, margin=dict(r=24, b=10),
                      legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="left", x=0))
    show_plot(fig)

    mejor_ahorro = max((o for o in ofertas if o[2] == "Ahorro e inversión"), key=lambda o: o[1])
    credito_barato = min((o for o in ofertas if o[2] == "Crédito"), key=lambda o: o[1])
    st.caption(
        f"Ofertas consultadas el 17 de octubre de 2026. Entre la mejor tasa de ahorro "
        f"({mejor_ahorro[1] * 100:.2f} % EA) y el crédito más barato ({credito_barato[1] * 100:.2f} % EA) hay "
        f"{(credito_barato[1] - mejor_ahorro[1]) * 100:.2f} puntos: la diferencia entre lo que el banco paga "
        "por ahorrar y lo que cobra por prestar."
    )

# ---------------------------------------------------------------------------
# DECISIONES DE LOS CASOS Y EQUIPO
# ---------------------------------------------------------------------------
st.write("")
section("Decisiones de los casos aplicados", "Se actualiza si cambias los datos en Casos aplicados.")
show_table(calcular_casos(params))

st.write("")
section("Equipo de trabajo")
EQUIPO = [
    ("Mariana Arbeláez", "Interés simple, interés compuesto, rentabilidad y equivalencia de tasas"),
    ("Evelyn Jiménez", "Series uniformes y gradientes (aritméticos y geométricos)"),
    ("María Lucía Cadavid", "Tablas de amortización, panel principal y consolidación de casos"),
]
cols = st.columns(3, gap="medium")
for col, (nombre, modulos) in zip(cols, EQUIPO):
    with col:
        with st.container(border=True):
            st.markdown(f"**{nombre}**")
            st.caption(modulos)
