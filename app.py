import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Tablero de Ingeniería Financiera | UPB",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS PERSONALIZADOS (Para darle un toque moderno y ejecutivo) ---
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 30px;
    }
    .card {
        background-color: #F8FAFC;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/bank-building.png", width=70)
    st.markdown("### **Ingeniería Financiera**")
    st.markdown("---")
    st.markdown("**📌 Navegación del Tablero**")
    st.markdown("Usa los módulos superiores para explorar los cálculos y modelos financieros.")
    st.markdown("---")
    st.markdown("**🎓 Datos Académicos**")
    st.markdown("- **Institución:** UPB")
    st.markdown("- **Docente:** Adriana Arango L.")
    st.markdown("- **Entrega:** 29 de Octubre, 2026")

# --- CUERPO PRINCIPAL ---
st.markdown('<p class="main-header">Tablero de Síntesis y Visualización Financiera</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Plataforma interactiva para el análisis de tasas, anualidades, gradientes, amortizaciones y casos de estudio reales.</p>', unsafe_allow_html=True)

# Tarjetas de Indicadores Principales (Métricas Clave)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Ponderación", value="20%", delta="Nota Final")
with col2:
    st.metric(label="Módulos Activos", value="6", delta="Temas del Curso")
with col3:
    st.metric(label="Casos Aplicados", value="3 Casos", delta="Evaluación Real")
with col4:
    st.metric(label="Estado", value="Operativo", delta="100% Trazable")

st.markdown("---")

# Sección de Estructura del Equipo y Módulos
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown("### 📊 Arquitectura del Módulo Financiero")
    st.write(
        "Este sistema integra de forma automatizada las principales herramientas de las matemáticas financieras, "
        "permitiendo modificar variables en tiempo real, visualizar comportamientos gráficos y auditar cada resultado "
        "bajo los estándares de la ingeniería financiera."
    )
    
    # Tabla resumen de temas
    import pandas as pd
    df_resumen = pd.DataFrame({
        "Módulo": [
            "1. Interés Simple y Compuesto", 
            "2. Rentabilidad y Tasas", 
            "3. Series Uniformes", 
            "4. Gradientes", 
            "5. Tablas de Amortización",
            "6. Casos Aplicados"
        ],
        "Enfoque": [
            "Crecimiento y despeje de variables",
            "Efectivas, nominales, anticipadas y retención",
            "Anualidades vencidas y anticipadas",
            "Aritméticos y geométricos",
            "Cuota fija vs abono constante",
            "Análisis de productos reales con decisión"
        ]
    })
    st.table(df_resumen)

with col_right:
    st.markdown("### 👥 Equipo de Trabajo")
    
    st.markdown("""
    <div class="card">
        <b>Integrante 1 (Tú)</b><br>
        • Interés Simple y Compuesto<br>
        • Rentabilidad y Equivalencia de Tasas
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <b>Integrante 2</b><br>
        • Series Uniformes<br>
        • Gradientes (Aritméticos y Geométricos)
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <b>Integrante 3</b><br>
        • Tablas de Amortización<br>
        • Panel Principal y Consolidación
    </div>
    """, unsafe_allow_html=True)

# Footer discreto y profesional
st.markdown("---")
st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 0.85rem;'>Universidad Pontificia Bolivariana — Escuela de Ingenierías</p>", unsafe_allow_html=True)