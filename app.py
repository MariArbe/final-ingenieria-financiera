import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.casos import DEFAULTS, calcular_caso1, calcular_caso2, calcular_caso3, calcular_casos
from utils.ui import (
    setup_page, page_header, section, kpi, callout, safe_page_link, show_table, show_plot, style_fig,
    money, pct, BLUSH, WINE,
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
p1, p2, p3 = params["c1"], params["c2"], params["c3"]
r1, r2, r3 = calcular_caso1(p1), calcular_caso2(p2), calcular_caso3(p3)

# ---------------------------------------------------------------------------
# RESULTADOS DESTACADOS
# ---------------------------------------------------------------------------
section("Resultados destacados", "Con las ofertas consultadas el 17 de octubre de 2026.")
m1, m2, ahorros = r1["mejor"], r2["mejor"], r1["prods"][1]
k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi(f"Mejor inversión · {m1['nombre']}", pct(m1["ea_neta"], 2),
        f"EA neta · {money(m1['neto'])} de ganancia en {p1['meses']} meses", accent=True)
with k2:
    if r2["iguales"]:
        kpi("Crédito · las dos opciones cuestan igual", pct(m2["ea"], 2), "Misma tasa efectiva anual")
    else:
        kpi(f"Crédito · elegir {m2['nombre']}", money(r2["ahorro_vp"]),
            f"Ahorro en valor presente · EA {pct(m2['ea'], 2)}")
with k3:
    kpi("Plan de ahorro · primera cuota", money(r3["a1"]),
        f"Para reunir {money(p3['meta'])} en {p3['meses']} meses")
with k4:
    kpi(ahorros["nombre"], money(ahorros["neto"]),
        f"Ganancia neta en {p1['meses']} meses, " + ("con cuota de manejo" if ahorros["costos"] > 0
                                                      else "sin cuota de manejo"))

st.write("")
col_graf, col_ver = st.columns([1.65, 1], gap="medium")

# ---------------------------------------------------------------------------
# TASAS DEL MERCADO CONSULTADO
# ---------------------------------------------------------------------------
with col_graf:
    ofertas = [
        (ahorros["nombre"], ahorros["ea"], "Ahorro e inversión"),
        ("Cajitas de ahorro Nu", p3["ea"] / 100, "Ahorro e inversión"),
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
        f"Entre la mejor tasa de ahorro ({mejor_ahorro[1] * 100:.2f} % EA) y el crédito más barato "
        f"({credito_barato[1] * 100:.2f} % EA) hay {(credito_barato[1] - mejor_ahorro[1]) * 100:.2f} puntos: "
        "la diferencia entre lo que el banco paga por ahorrar y lo que cobra por prestar."
    )

# ---------------------------------------------------------------------------
# VERIFICACIÓN GLOBAL
# ---------------------------------------------------------------------------
with col_ver:
    verif = verificar_todo(params)
    total = sum(v["Pruebas"] for v in verif)
    ok = sum(v["Coinciden"] for v in verif)
    kpi("Verificaciones que coinciden", f"{ok} de {total}",
        "Cálculo del tablero frente al cálculo manual, en los cinco módulos")
    st.write("")
    show_table(
        pd.DataFrame([
            {"Módulo": v["Módulo"], "Pruebas": v["Pruebas"],
             "Estado": "✅ Coincide" if not v["fallas"] else f"❌ Revisar ({len(v['fallas'])})"}
            for v in verif
        ])
    )
    fallas = [f"{v['Módulo']}: {f}" for v in verif for f in v["fallas"]]
    if fallas:
        callout("No coinciden: " + "; ".join(fallas[:5]) + ("…" if len(fallas) > 5 else ""), "warn")

# ---------------------------------------------------------------------------
# MÓDULOS
# ---------------------------------------------------------------------------
st.write("")
section("Módulos", "Elige un módulo para modificar parámetros y ver los resultados al instante.")

MODULOS = [
    ("📈", "Interés simple y compuesto", "Simulación, comparación gráfica y despeje de tasa y plazo.",
     "pages/1_Interes_Simple_y_Compuesto.py"),
    ("💱", "Rentabilidad y tasas", "Equivalencias, tasas combinadas y retención en la fuente.",
     "pages/2_Rentabilidad_y_Tasas.py"),
    ("🔁", "Series y gradientes", "Anualidades vencidas y anticipadas; gradientes aritméticos y geométricos.",
     "pages/3_Series_y_Gradientes.py"),
    ("🧾", "Tablas de amortización", "Cuota fija y abono constante, abonos extra, refinanciación e inflación.",
     "pages/4_Tablas_de_Amortizacion.py"),
    ("🧭", "Casos aplicados", "CDT, crédito y plan de ahorro con ofertas reales, y la decisión recomendada.",
     "pages/5_Casos_Aplicados.py"),
]
for fila in (MODULOS[:3], MODULOS[3:]):
    cols = st.columns(len(fila), gap="medium")   # 3 + 2: cada fila ocupa todo el ancho
    for col, (icono, nombre, desc, ruta) in zip(cols, fila):
        with col:
            with st.container(border=True):
                st.markdown(f"**{icono} {nombre}**")
                st.caption(desc)
                safe_page_link(ruta, label="Abrir módulo")

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

st.write("")
section("Resumen de casos aplicados", "Se actualiza si cambias los datos en Casos aplicados.")
show_table(calcular_casos(params))
