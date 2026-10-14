import streamlit as st

st.set_page_config(
    page_title="Tablero de Ingeniería Financiera - UPB",
    page_icon="📈",
    layout="wide"
)

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/combo-chart--v1.png", width=80)
    st.title("Ingeniería Financiera")
    st.markdown("**Docente:** Adriana Arango L.")
    st.markdown("**Institución:** UPB")
    st.markdown("---")
    st.info("💡 **Instrucción:** Usa este menú para moverte entre los módulos temáticos y los casos aplicados.")

# --- CUERPO PRINCIPAL ---
st.title("📊 Tablero de Visualización y Síntesis Financiera")
st.markdown("### Síntesis de interés, rentabilidad, series uniformes, gradientes y amortización.")
st.markdown("---")

# Métricas o tarjetas informativas iniciales
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.metric(label="Ponderación del Taller", value="20%", delta="Nota del curso")
with col_info2:
    st.metric(label="Fecha de Entrega", value="29 Oct 2026", delta="Jueves en clase")
with col_info3:
    st.metric(label="Modalidad", value="Equipos (3 máx)", delta="Sustentación en vivo")

st.markdown("---")
st.subheader("👥 Distribución de Módulos en el Equipo")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("### 👩‍💻 Integrante 1 (Tú)")
    st.markdown("""
    * Módulo de Interés Simple
    * Módulo de Interés Compuesto
    * Módulo de Rentabilidad y Equivalencia de Tasas
    """)

with c2:
    st.markdown("### 👩‍💻 Integrante 2")
    st.markdown("""
    * Módulo de Series Uniformes (Vencidas y Anticipadas)
    * Módulo de Gradientes (Aritméticos y Geométricos)
    """)

with c3:
    st.markdown("### 👩‍💻 Integrante 3")
    st.markdown("""
    * Panel Principal (`app.py`)
    * Módulo de Tablas de Amortización (Cuota fija / Abono constante)
    * Coordinación de Casos Aplicados
    """)

st.markdown("---")
st.subheader("📌 Objetivo del Tablero")
st.write("""
Este tablero interactivo sintetiza los conceptos fundamentales de la ingeniería financiera para analizar casos aplicados 
de productos e inversiones reales. Todos los cálculos son dinámicos, trazables mediante código visible, y permiten 
modificar parámetros de entrada para evaluar escenarios en tiempo real.
""")