import streamlit as st

from utils.ui import setup_page, page_header, section, kpi, callout, safe_page_link

setup_page("Tablero de Ingeniería Financiera", "💎")
page_header(
    "Tablero de síntesis y visualización financiera",
    "Interés, rentabilidad, series uniformes, gradientes y amortización, aplicados a productos "
    "e inversiones financieras reales.",
)

k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi("Ponderación", "20%", "de la nota del curso")
with k2:
    kpi("Entrega y presentación", "29 oct 2026", "en el horario de clase")
with k3:
    kpi("Equipo", "3 integrantes", "cada uno explica cualquier módulo")
with k4:
    kpi("Casos aplicados", "3 mínimo", "deben usar los seis temas", accent=True)

st.write("")
section("Módulos", "Elige un módulo para modificar parámetros y ver los resultados al instante.")

MODULOS = [
    ("📈", "Interés simple y compuesto", "Simulación, comparación gráfica y despeje de tasa y plazo.",
     "pages/1_Interes_Simple_y_Compuesto.py"),
    ("💱", "Rentabilidad y tasas", "Equivalencias, tasas combinadas y retención en la fuente.",
     "pages/2_Rentabilidad_y_Tasas.py"),
    ("🔁", "Series y gradientes", "Anualidades vencidas y anticipadas; gradientes aritméticos y geométricos.",
     "pages/3_Series_y_Gradientes.py"),
    ("🧾", "Tablas de amortización", "Cuota fija y abono constante a capital, con verificación de saldo cero.",
     "pages/4_Tablas_de_Amortizacion.py"),
    ("🧭", "Casos aplicados", "CDT, crédito y plan de ahorro, con la decisión recomendada.",
     "pages/5_Casos_Aplicados.py"),
]
for fila in (MODULOS[:3], MODULOS[3:]):
    cols = st.columns(3, gap="medium")
    for col, (icono, nombre, desc, ruta) in zip(cols, fila):
        with col:
            with st.container(border=True):
                st.markdown(f"**{icono} {nombre}**")
                st.caption(desc)
                safe_page_link(ruta, label="Abrir módulo")

st.write("")
col_eq, col_info = st.columns([1.2, 1], gap="large")
with col_eq:
    section("Equipo de trabajo")
    EQUIPO = [
        ("Mariana Arbeláez", "Interés simple, interés compuesto, rentabilidad y equivalencia de tasas"),
        ("Evelyn Jiménez", "Series uniformes y gradientes (aritméticos y geométricos)"),
        ("María Lucía Cadavid", "Tablas de amortización, panel principal y consolidación de casos"),
    ]
    for nombre, modulos in EQUIPO:
        with st.container(border=True):
            st.markdown(f"**{nombre}**")
            st.caption(modulos)
with col_info:
    section("Resumen de casos aplicados")
    callout("Aquí se mostrará, por caso, el producto, la tasa efectiva anual, el valor total pagado o "
            "recibido y la decisión recomendada. Se alimenta desde la página Casos aplicados.", "info")