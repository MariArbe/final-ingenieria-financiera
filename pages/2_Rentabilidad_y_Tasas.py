import streamlit as st
import pandas as pd
from utils.financial_math import nominal_a_efectiva, vencida_a_anticipada, tasa_combinada, rentabilidad_neta

st.title("🔄 Módulo de Rentabilidad y Equivalencia de Tasas")

st.subheader("1. Conversión de Tasas y Tasas Combinadas")
col1, col2 = st.columns(2)

with col1:
    j_nom = st.number_input("Tasa Nominal Anual (%)", value=24.0) / 100.0
    m_val = st.selectbox("Periodicidad de Capitalización", [1, 2, 4, 6, 12, 360], format_func=lambda x: {1:"Anual", 2:"Semestral", 4:"Trimestral", 6:"Bimestral", 12:"Mensual", 360:"Diaria"}[x])
    ea_calc = nominal_a_efectiva(j_nom, m_val)
    st.metric("Tasa Efectiva Anual (EA)", f"{ea_calc*100:.4f}%")

with col2:
    inf = st.number_input("Inflación Anual (%)", value=5.0) / 100.0
    pts = st.number_input("Puntos Adicionales (%)", value=4.0) / 100.0
    t_comb = tasa_combinada(inf, pts)
    st.metric("Tasa Combinada (Inflación + Puntos)", f"{t_comb*100:.4f}%")

st.markdown("---")
st.subheader("2. Rentabilidad Neta con Retención en la Fuente")
col_r1, col_r2 = st.columns(2)
with col_r1:
    tea_base = st.number_input("Tasa Efectiva Anual de Retorno (%)", value=12.0) / 100.0
    retencion = st.number_input("Tasa de Retención en la Fuente (%)", value=4.0) / 100.0
with col_r2:
    tea_neta = rentabilidad_neta(tea_base, retencion)
    st.metric("Tasa Efectiva Anual Neta", f"{tea_neta*100:.4f}%", help="Descontando la retención en la fuente")

st.markdown("---")
st.subheader("3. Tabla de Equivalencias Automática")
tasas_ejemplo = [0.01, 0.015, 0.02, 0.025, 0.03]
data_eq = []
for t in tasas_ejemplo:
    ea_val = (1 + t)**12 - 1
    nominal_mes = t * 12
    anticipada = vencida_a_anticipada(t)
    data_eq.append({
        "Tasa Mes Vencida (MV)": f"{t*100:.2f}%",
        "Efectiva Anual (EA)": f"{ea_val*100:.2f}%",
        "Nominal Anual Mes Vencido (NAMV)": f"{nominal_mes*100:.2f}%",
        "Tasa Mes Anticipada (MA)": f"{anticipada*100:.2f}%"
    })

df_equivalencias = pd.DataFrame(data_eq)
st.table(df_equivalencias)
