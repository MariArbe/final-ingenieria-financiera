import streamlit as st

st.set_page_config(
    page_title="Tablero de Ingeniería Financiera",
    page_icon="📈",
    layout="wide"
)

st.title("📊 Tablero de Visualización y Síntesis Financiera")
st.markdown("### Curso: Ingeniería Financiera - UPB")

st.info("👈 Utiliza el menú lateral izquierdo para navegar entre los diferentes módulos y casos aplicados.")

st.markdown("---")
st.subheader("👥 Integrantes del Equipo")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Integrante 1**")
    st.markdown("Interés simple, compuesto, rentabilidad y tasas.")
with col2:
    st.markdown("**Integrante 2**")
    st.markdown("Series uniformes y gradientes.")
with col3:
    st.markdown("**Integrante 3**")
    st.markdown("Tablas de amortización y Panel Principal.")

st.markdown("---")
st.subheader("📋 Resumen Ejecutivo de Casos Aplicados")
st.write("En la sección de **Casos Aplicados** en el menú lateral encontrarás el desarrollo de los escenarios financieros reales evaluados por el equipo.")
