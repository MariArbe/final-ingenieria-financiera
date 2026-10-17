import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.financial_math import (
    interes_simple, interes_compuesto,
    despejar_tasa_compuesto, despejar_plazo_compuesto,
    despejar_tasa_simple, despejar_plazo_simple,
    valor_presente_simple, valor_presente_compuesto,
)
from utils.ui import (
    setup_page, page_header, section, kpi, callout, style_fig,
    show_plot, show_table, verification_table, money, STONE, WINE, WINE_FILL,
)

setup_page("Interés simple y compuesto", "📈")
page_header(
    "Interés simple y compuesto",
    "Compara cómo crece el mismo capital bajo cada régimen y despeja la tasa, el plazo, "
    "el valor futuro o el valor presente para llegar a una meta.",
)

UNIDADES = {
    "Mensual": ("mes", "meses"),
    "Bimestral": ("bimestre", "bimestres"),
    "Trimestral": ("trimestre", "trimestres"),
    "Semestral": ("semestre", "semestres"),
    "Anual": ("año", "años"),
}

tab_sim, tab_des, tab_ver = st.tabs(["Simulación", "Despeje de variables", "Supuestos y verificación"])

# ---------------------------------------------------------------------------
# 1) SIMULACIÓN
# ---------------------------------------------------------------------------
with tab_sim:
    col_in, col_out = st.columns([1, 2.4], gap="large")

    with col_in:
        with st.container(border=True):
            section("Parámetros", "Los resultados se recalculan al cambiar cualquier valor.")
            capital = st.number_input("Capital inicial ($)", min_value=100.0, value=1_000_000.0,
                                      step=50_000.0, format="%.2f")
            unidad = st.selectbox("Unidad de tiempo", list(UNIDADES))
            tasa_pct = st.number_input(f"Tasa {unidad.lower()} (%)", min_value=0.01, value=2.5,
                                       step=0.1, format="%.2f")
            periodos = st.number_input(f"Plazo (número de {UNIDADES[unidad][1]})",
                                       min_value=1, max_value=600, value=12, step=1)
            convencion = st.selectbox("Convención de días", ["30/360", "Actual/365"],
                                      help="Se usa en interés simple cuando el plazo se expresa en días.")

    tasa = tasa_pct / 100.0
    per_list = list(range(int(periodos) + 1))
    vals_s = [interes_simple(capital, tasa, p, convencion)[0] for p in per_list]
    vals_c = [interes_compuesto(capital, tasa, p)[0] for p in per_list]
    vf_s, int_s = interes_simple(capital, tasa, periodos, convencion)
    vf_c, int_c = interes_compuesto(capital, tasa, periodos)
    dif = vf_c - vf_s

    with col_out:
        k1, k2, k3 = st.columns(3)
        with k1:
            kpi("Valor futuro · interés simple", money(vf_s), f"Intereses: {money(int_s)}")
        with k2:
            kpi("Valor futuro · interés compuesto", money(vf_c), f"Intereses: {money(int_c)}")
        with k3:
            kpi("Ventaja del compuesto", money(dif),
                f"{dif / int_s * 100:,.1f}% más intereses que el simple", accent=True)

        st.write("")
        fig = go.Figure()
        fig.add_scatter(x=per_list, y=vals_s, name="Interés simple", mode="lines+markers",
                        line=dict(color=STONE, width=3), marker=dict(size=6))
        fig.add_scatter(x=per_list, y=vals_c, name="Interés compuesto", mode="lines+markers",
                        line=dict(color=WINE, width=3), marker=dict(size=6))
        fig.update_yaxes(tickprefix="$", tickformat=",.0f")
        style_fig(fig, "Crecimiento del capital: simple vs. compuesto",
                  f"Tiempo ({UNIDADES[unidad][1]})", "Valor acumulado (COP)")
        show_plot(fig)

        brecha = [c - s for c, s in zip(vals_c, vals_s)]
        fig2 = go.Figure()
        fig2.add_scatter(x=per_list, y=brecha, name="Compuesto − simple", mode="lines",
                         fill="tozeroy", line=dict(color=WINE, width=2),
                         fillcolor=WINE_FILL)
        fig2.update_yaxes(tickprefix="$", tickformat=",.0f")
        style_fig(fig2, "Diferencia acumulada entre regímenes",
                  f"Tiempo ({UNIDADES[unidad][1]})", "Diferencia (COP)")
        fig2.update_layout(height=300, showlegend=False)
        show_plot(fig2)

        with st.expander("Ver tabla periodo a periodo"):
            df = pd.DataFrame({
                "Periodo": per_list,
                "Valor simple ($)": vals_s,
                "Valor compuesto ($)": vals_c,
                "Diferencia ($)": brecha,
            })
            show_table(df, column_config={
                c: st.column_config.NumberColumn(format="$%.2f")
                for c in ["Valor simple ($)", "Valor compuesto ($)", "Diferencia ($)"]
            })

# ---------------------------------------------------------------------------
# 2) DESPEJE
# ---------------------------------------------------------------------------
with tab_des:
    col_in, col_out = st.columns([1, 2.4], gap="large")

    with col_in:
        with st.container(border=True):
            section("¿Qué quieres encontrar?")
            regimen = st.radio("Régimen", ["Compuesto", "Simple"], horizontal=True)
            objetivo = st.selectbox("Variable a despejar",
                                    ["Tasa", "Plazo", "Valor futuro", "Valor presente"])
            c = vf = i = n = None
            if objetivo == "Tasa":
                c = st.number_input("Capital inicial ($)", min_value=1.0, value=1_000_000.0, step=50_000.0, key="t_c")
                vf = st.number_input("Valor futuro deseado ($)", min_value=1.0, value=1_300_000.0, step=50_000.0, key="t_vf")
                n = st.number_input("Número de periodos", min_value=1, value=12, step=1, key="t_n")
            elif objetivo == "Plazo":
                c = st.number_input("Capital inicial ($)", min_value=1.0, value=1_000_000.0, step=50_000.0, key="p_c")
                vf = st.number_input("Valor futuro deseado ($)", min_value=1.0, value=1_500_000.0, step=50_000.0, key="p_vf")
                i = st.number_input("Tasa periódica (%)", min_value=0.01, value=2.0, step=0.1, key="p_i") / 100
            elif objetivo == "Valor futuro":
                c = st.number_input("Capital inicial ($)", min_value=1.0, value=1_000_000.0, step=50_000.0, key="f_c")
                i = st.number_input("Tasa periódica (%)", min_value=0.01, value=2.0, step=0.1, key="f_i") / 100
                n = st.number_input("Número de periodos", min_value=1, value=12, step=1, key="f_n")
            else:
                vf = st.number_input("Valor futuro ($)", min_value=1.0, value=1_500_000.0, step=50_000.0, key="v_vf")
                i = st.number_input("Tasa periódica (%)", min_value=0.01, value=2.0, step=0.1, key="v_i") / 100
                n = st.number_input("Número de periodos", min_value=1, value=12, step=1, key="v_n")

    simple = regimen == "Simple"
    titulo = valor_txt = formula = comprobacion = aviso = None

    if objetivo == "Tasa":
        r = despejar_tasa_simple(c, vf, n) if simple else despejar_tasa_compuesto(c, vf, n)
        titulo, valor_txt = "Tasa periódica requerida", f"{r * 100:.4f}%"
        formula = r"i=\frac{VF/C-1}{n}" if simple else r"i=\left(\frac{VF}{C}\right)^{1/n}-1"
        chk = interes_simple(c, r, n)[0] if simple else interes_compuesto(c, r, n)[0]
        comprobacion = f"Con esa tasa, el capital llega a {money(chk, 2)} en {n} periodos."
    elif objetivo == "Plazo":
        if vf <= c:
            aviso = "El valor futuro debe ser mayor al capital para despejar el plazo."
        else:
            r = despejar_plazo_simple(c, vf, i) if simple else despejar_plazo_compuesto(c, vf, i)
            titulo, valor_txt = "Plazo requerido", f"{r:,.2f} periodos"
            formula = r"n=\frac{VF/C-1}{i}" if simple else r"n=\frac{\ln(VF/C)}{\ln(1+i)}"
            chk = interes_simple(c, i, r)[0] if simple else interes_compuesto(c, i, r)[0]
            comprobacion = f"Con ese plazo, el capital llega a {money(chk, 2)}."
    elif objetivo == "Valor futuro":
        r = interes_simple(c, i, n)[0] if simple else interes_compuesto(c, i, n)[0]
        titulo, valor_txt = "Valor futuro", money(r, 2)
        formula = r"VF=C(1+i\,n)" if simple else r"VF=C(1+i)^n"
        comprobacion = f"Intereses generados: {money(r - c, 2)}."
    else:
        r = valor_presente_simple(vf, i, n) if simple else valor_presente_compuesto(vf, i, n)
        titulo, valor_txt = "Valor presente", money(r, 2)
        formula = r"VP=\frac{VF}{1+i\,n}" if simple else r"VP=\frac{VF}{(1+i)^n}"
        comprobacion = f"Hoy equivale a {money(r, 2)} para recibir {money(vf, 2)} dentro de {n} periodos."

    with col_out:
        if aviso:
            callout(aviso, "warn")
        else:
            kpi(titulo, valor_txt, f"Régimen: interés {regimen.lower()}", accent=True)
            st.write("")
            section("Fórmula aplicada")
            st.latex(formula)
            callout(comprobacion, "info")

# ---------------------------------------------------------------------------
# 3) SUPUESTOS Y VERIFICACIÓN
# ---------------------------------------------------------------------------
with tab_ver:
    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        with st.container(border=True):
            section("Supuestos")
            st.markdown(
                f"- **Tipo de tasa:** periódica efectiva, vencida.\n"
                f"- **Periodicidad:** {unidad.lower()} (la tasa y el plazo usan la misma unidad).\n"
                f"- **Convención de días (interés simple):** {convencion}.\n"
                "- **Capitalización:** en interés compuesto los intereses se reinvierten cada periodo.\n"
                "- **Moneda:** pesos colombianos (COP)."
            )
    with col_b:
        with st.container(border=True):
            section("Fórmulas empleadas")
            st.latex(r"VF_{simple}=C(1+i\,n)\qquad VF_{comp}=C(1+i)^n")
            st.latex(r"VP_{simple}=\frac{VF}{1+i\,n}\qquad VP_{comp}=\frac{VF}{(1+i)^n}")

    st.write("")
    section("Verificación contra cálculo manual",
            "Se usan los parámetros de la pestaña Simulación.")
    filas = [
        ("VF compuesto = C·(1+i)ⁿ", vf_c, capital * (1 + tasa) ** periodos),
        ("VF simple = C·(1+i·n)", vf_s, capital * (1 + tasa * periodos)),
        ("Intereses compuestos = VF − C", int_c, vf_c - capital),
        ("Despeje de tasa (ida y vuelta)", despejar_tasa_compuesto(capital, vf_c, periodos), tasa),
        ("Despeje de plazo (ida y vuelta)", despejar_plazo_compuesto(capital, vf_c, tasa), float(periodos)),
    ]
    verification_table(filas)