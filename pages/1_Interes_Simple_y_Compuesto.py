import streamlit as st
import pandas as pd
import plotly.express as px
from utils.financial_math import interes_simple, interes_compuesto, despejar_tasa_compuesto, despejar_plazo_compuesto

st.title("📈 Módulo de Interés Simple e Interés Compuesto")

tab1, tab2 = st.tabs(["Cálculo y Gráfica Comparativa", "Despeje de Tasas y Plazos"])

with tab1:
    st.subheader("Simulación y Crecimiento Acumulado")
    col1, col2 = st.columns(2)
    
    with col1:
        capital = st.number_input("Capital Inicial ($)", min_value=100.0, value=1000000.0, step=50000.0)
        tasa_pct = st.number_input("Tasa de Interés Periódica (%)", min_value=0.0, value=2.5, step=0.1)
        tasa = tasa_pct / 100.0
    with col2:
        periodos = st.number_input("Número de Periodos", min_value=1, value=12, step=1)
        convencion = st.selectbox("Convención de Días (Interés Simple)", ["30/360", "Actual/365"])

    # Cálculos
    per_list = list(range(periodos + 1))
    vals_simple = [interes_simple(capital, tasa, p)[0] for p in per_list]
    vals_compuesto = [interes_compuesto(capital, tasa, p)[0] for p in per_list]

    vf_s, int_s = interes_simple(capital, tasa, periodos)
    vf_c, int_c = interes_compuesto(capital, tasa, periodos)

    # Métricas en pantalla
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Valor Futuro (Interés Simple)", f"${vf_s:,.2f}", f"Intereses: ${int_s:,.2f}")
    with col_m2:
        st.metric("Valor Futuro (Interés Compuesto)", f"${vf_c:,.2f}", f"Intereses: ${int_c:,.2f}")

    # Gráfica interactiva con Plotly
    df_plot = pd.DataFrame({
        "Periodo": per_list * 2,
        "Valor Acumulado": vals_simple + vals_compuesto,
        "Régimen": ["Interés Simple"] * len(per_list) + ["Interés Compuesto"] * len(per_list)
    })

    fig = px.line(df_plot, x="Periodo", y="Valor Acumulado", color="Régimen", 
                  markers=True, title="Evolución del Valor Acumulado en el Tiempo")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Despeje de Variables (Interés Compuesto)")
    tipo_despeje = st.radio("¿Qué variable deseas despejar?", ["Tasa de Interés", "Número de Periodos"])
    
    if tipo_despeje == "Tasa de Interés":
        c_in = st.number_input("Capital Inicial ($)", value=1000000.0, key="dc")
        vf_in = st.number_input("Valor Futuro Deseado ($)", value=1300000.0, key="dvf")
        n_in = st.number_input("Número de Periodos", value=12, key="dn")
        if st.button("Calcular Tasa"):
            tasa_res = despejar_tasa_compuesto(c_in, vf_in, n_in)
            st.success(f"La tasa periódica requerida es: **{tasa_res*100:.4f}%**")
    else:
        c_in2 = st.number_input("Capital Inicial ($)", value=1000000.0, key="dc2")
        vf_in2 = st.number_input("Valor Futuro Deseado ($)", value=1500000.0, key="dvf2")
        t_in2 = st.number_input("Tasa Periódica (%)", value=2.0, key="dt2") / 100.0
        if st.button("Calcular Plazo"):
            n_res = despejar_plazo_compuesto(c_in2, vf_in2, t_in2)
            st.success(f"El número de periodos necesarios es: **{n_res:.2f} periodos**")
