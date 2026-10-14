import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Tablero de Ingeniería Financiera | UPB",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS PERSONALIZADOS (Paleta Rosa Formal / Rose Gold & Minimalista) ---
st.markdown("""
    <style>
    /* Estilos globales y tipografía */
    .main {
        background-color: #FAFAF9;
    }
    .main-header {
        font-size: 2.4rem;
        color: #881337; /* Vinotinto / Rosa formal profundo */
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.15rem;
        color: #57534E;
        margin-bottom: 25px;
        font-weight: 400;
    }
    /* Tarjetas de equipo y arquitectura */
    .card-team {
        background: linear-gradient(135deg, #FFF1F2 0%, #FFE4E6 100%);
        padding: 22px;
        border-radius: 12px;
        border: 1px solid #FECDD3;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(244, 63, 94, 0.05);
    }
    .card-team h4 {
        color: #9F1239;
        margin-top: 0px;
        font-weight: 700;
    }
    .card-team p {
        color: #44403C;
        margin-bottom: 0px;
        font-size: 0.95rem;
    }
    /* Estilo para las métricas */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E7E5E4;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("### 💎 Ingeniería Financiera")
    st.markdown("<p style='color: #78716C; font-size: 0.85rem;'>Universidad Pontificia Bolivariana</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Panel de Control**")
    st.markdown("Selecciona un módulo en la parte superior o lateral para iniciar las simulaciones.")
    st.markdown("---")
    st.markdown("**Detalles de Entrega**")
    st.markdown("• **Fecha:** Jueves, 29 de Octubre 2026")
    st.markdown("• **Docente:** Adriana Arango L.")
    st.markdown("• **Ponderación:** 20% de la nota")

# --- CUERPO PRINCIPAL ---
st.markdown('<p class="main-header">Tablero de Síntesis y Visualización Financiera</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Plataforma analítica para la evaluación de tasas, anualidades, gradientes, amortizaciones y casos de estudio reales.</p>', unsafe_allow_html=True)

# Métricas Ejecutivas Superiores
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Evaluación", value="20%", delta="Nota Definitiva")
with col2:
    st.metric(label="Módulos Teóricos", value="5 Módulos", delta="Cobertura Total")
with col3:
    st.metric(label="Casos Aplicados", value="3 Casos", delta="Análisis Real")
with col4:
    st.metric(label="Trazabilidad", value="100%", delta="Código y Fórmulas")

st.markdown("---")

# Distribución en dos columnas: Integrantes y Arquitectura
col_left, col_right = st.columns([1.1, 1])

with col_left:
    st.markdown("### 👩‍💻 Equipo de Trabajo")
    
    st.markdown("""
    <div class="card-team">
        <h4>Mariana Arbeláez</h4>
        <p><b>Módulos a cargo:</b> Interés Simple, Interés Compuesto, Rentabilidad y Equivalencia de Tasas.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card-team">
        <h4>Evelyn Jiménez</h4>
        <p><b>Módulos a cargo:</b> Series Uniformes (Anualidades) y Gradientes (Aritméticos y Geométricos).</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card-team">
        <h4>María Lucía Cadavid</h4>
        <p><b>Módulos a cargo:</b> Tablas de Amortización, Panel Principal y Consolidación de Casos.</p>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("### 🗂️ Arquitectura del Sistema")
    st.write(
        "El tablero está estructurado bajo un diseño modular y escalable en Python (Streamlit), "
        "garantizando cálculos precisos, trazables y parametrizables en tiempo real para la toma de decisiones financieras."
    )
    
    # Tabla resumen ejecutiva limpia
    df_arq = pd.DataFrame({
        "Módulo": [
            "1. Interés Simple / Compuesto",
            "2. Rentabilidad y Tasas",
            "3. Series Uniformes",
            "4. Gradientes",
            "5. Tablas de Amortización",
            "6. Casos Aplicados"
        ],
        "Componente": [
            "Crecimiento y despeje",
            "EA, nominales y retención",
            "Vencidas y anticipadas",
            "Crecimiento lineal/geométrico",
            "Cuota fija vs abono constante",
            "Análisis de portafolios reales"
        ]
    })
    st.dataframe(df_arq, use_container_width=True, hide_index=True)

# Footer elegante
st.markdown("---")
st.markdown("<p style='text-align: center; color: #A8A29E; font-size: 0.85rem;'>Escuela de Ingenierías — Facultad de Ingeniería Financiera</p>", unsafe_allow_html=True)