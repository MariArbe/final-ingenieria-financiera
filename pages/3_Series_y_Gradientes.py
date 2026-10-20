import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from utils.financial_math import (
    vp_serie, vf_serie, cuota_desde_vp, cuota_desde_vf, factor_vf_serie, factor_vp_serie,
    flujos_gradiente_aritmetico, flujos_gradiente_geometrico, vp_flujos, vf_flujos,
    vp_gradiente_aritmetico_formula, vp_gradiente_geometrico_formula, cuota_desde_vp as cuota_eq_desde_vp,
)
from utils.ui import (
    setup_page, page_header, section, kpi, callout, style_fig,
    show_plot, show_table, verification_table, money, STONE, WINE, BLUSH,
)

setup_page("Series y gradientes", "🔁")
page_header(
    "Series uniformes y gradientes",
    "Calcula valor presente, valor futuro y cuota de series vencidas y anticipadas, y de gradientes "
    "aritméticos y geométricos, con el flujo de pagos a la vista.",
)

tab_ser, tab_gra, tab_ver = st.tabs(["Series uniformes", "Gradientes", "Supuestos y verificación"])

# ---------------------------------------------------------------------------
# 1) SERIES UNIFORMES
# ---------------------------------------------------------------------------
with tab_ser:
    col_in, col_out = st.columns([1, 2.4], gap="large")
    with col_in:
        with st.container(border=True):
            section("Parámetros", "Elige qué dato conoces; el módulo calcula los otros dos.")
            tipo_s = st.radio("Tipo de serie", ["Vencida", "Anticipada"], horizontal=True, key="s_tipo")
            conocido = st.selectbox("Dato conocido", ["Cuota", "Valor presente", "Valor futuro"], key="s_con")
            valor_s = st.number_input(f"{conocido} ($)", min_value=1.0,
                                      value={"Cuota": 500_000.0, "Valor presente": 10_000_000.0,
                                             "Valor futuro": 15_000_000.0}[conocido],
                                      step=50_000.0, key=f"s_val_{conocido}")
            i_s = st.number_input("Tasa periódica (%)", min_value=0.01, value=1.5, step=0.1, key="s_i") / 100
            n_s = st.number_input("Número de periodos", min_value=1, max_value=600, value=24, step=1, key="s_n")

    ant = tipo_s == "Anticipada"
    if conocido == "Cuota":
        cuota_s = valor_s
        vp_s, vf_s = vp_serie(cuota_s, i_s, n_s, ant), vf_serie(cuota_s, i_s, n_s, ant)
    elif conocido == "Valor presente":
        vp_s = valor_s
        cuota_s = cuota_desde_vp(vp_s, i_s, n_s, ant)
        vf_s = vp_s * (1 + i_s) ** n_s
    else:
        vf_s = valor_s
        cuota_s = cuota_desde_vf(vf_s, i_s, n_s, ant)
        vp_s = vf_s / (1 + i_s) ** n_s

    with col_out:
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            kpi("Cuota", money(cuota_s, 2), f"Serie {tipo_s.lower()}", accent=True)
        with k2:
            kpi("Valor presente", money(vp_s, 2))
        with k3:
            kpi("Valor futuro", money(vf_s, 2))
        with k4:
            kpi("Intereses implícitos", money(vf_s - cuota_s * n_s, 2), f"Total pagado: {money(cuota_s * n_s)}")

        st.write("")
        periodos = list(range(1, int(n_s) + 1))
        factor = 1 + i_s if ant else 1
        acumulado = [cuota_s * factor_vf_serie(i_s, k) * factor for k in periodos]
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.10,
                            subplot_titles=("Pago por periodo", "Valor acumulado de la serie"))
        fig.add_bar(x=periodos, y=[cuota_s] * len(periodos), name="Pago del periodo",
                    marker_color=BLUSH, row=1, col=1)
        fig.add_scatter(x=periodos, y=acumulado, name="Valor acumulado", mode="lines",
                        line=dict(color=WINE, width=3), row=2, col=1)
        style_fig(fig, "Flujo de pagos y valor acumulado de la serie", "Periodo", "Pago (COP)")
        fig.update_yaxes(tickprefix="$", tickformat=",.0f", title_text="Pago (COP)",
                         rangemode="tozero", row=1, col=1)
        fig.update_yaxes(tickprefix="$", tickformat=",.0f", title_text="Acumulado (COP)",
                         rangemode="tozero", row=2, col=1)
        fig.update_xaxes(title_text="", row=1, col=1)
        fig.update_xaxes(title_text="Periodo", row=2, col=1)
        fig.update_layout(height=560, showlegend=False)
        show_plot(fig)

# ---------------------------------------------------------------------------
# 2) GRADIENTES
# ---------------------------------------------------------------------------
with tab_gra:
    col_in, col_out = st.columns([1, 2.4], gap="large")
    with col_in:
        with st.container(border=True):
            section("Parámetros", "Flujos vencidos: la primera cuota cae al final del periodo 1.")
            tipo_g = st.radio("Tipo de gradiente", ["Aritmético", "Geométrico"], horizontal=True, key="g_tipo")
            a1 = st.number_input("Primera cuota ($)", min_value=1.0, value=300_000.0, step=10_000.0, key="g_a1")
            if tipo_g == "Aritmético":
                grad = st.number_input("Gradiente (G, $ por periodo)", value=20_000.0, step=5_000.0, key="g_G")
            else:
                grad = st.number_input("Gradiente (g, % por periodo)", value=1.0, step=0.1, key="g_g") / 100
            i_g = st.number_input("Tasa periódica (%)", min_value=0.01, value=1.5, step=0.1, key="g_i") / 100
            n_g = st.number_input("Número de periodos", min_value=2, max_value=600, value=24, step=1, key="g_n")

    flujos = (flujos_gradiente_aritmetico(a1, grad, n_g) if tipo_g == "Aritmético"
              else flujos_gradiente_geometrico(a1, grad, n_g))
    vp_g, vf_g = vp_flujos(flujos, i_g), vf_flujos(flujos, i_g)
    cuota_eq = cuota_eq_desde_vp(vp_g, i_g, n_g)

    with col_out:
        if (flujos < 0).any():
            callout("Con estos parámetros alguna cuota es negativa. Revisa el gradiente.", "warn")
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            kpi("Valor presente", money(vp_g, 2), accent=True)
        with k2:
            kpi("Valor futuro", money(vf_g, 2))
        with k3:
            kpi("Cuota uniforme equivalente", money(cuota_eq, 2), "misma VP, mismos periodos")
        with k4:
            kpi("Última cuota", money(flujos[-1], 2), f"Total pagado: {money(flujos.sum())}")

        st.write("")
        periodos_g = list(range(1, int(n_g) + 1))
        acumulado_g = [sum(flujos[j] * (1 + i_g) ** (k - j - 1) for j in range(k)) for k in periodos_g]
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.10,
                            subplot_titles=("Cuota por periodo", "Valor acumulado"))
        fig.add_bar(x=periodos_g, y=flujos, name="Cuota del periodo", marker_color=BLUSH, row=1, col=1)
        fig.add_hline(y=cuota_eq, line_dash="dash", line_color=WINE, line_width=2,
                      annotation_text=f"Cuota uniforme equivalente: {money(cuota_eq)}",
                      annotation_position="top left",
                      annotation_font=dict(color=WINE, size=12),
                      annotation_bgcolor="rgba(255,255,255,0.85)",
                      row=1, col=1)
        fig.add_scatter(x=periodos_g, y=acumulado_g, name="Valor acumulado", mode="lines",
                        line=dict(color=WINE, width=3), row=2, col=1)
        style_fig(fig, f"Flujo de cuotas y valor acumulado — gradiente {tipo_g.lower()}", "Periodo", "Cuota (COP)")
        fig.update_yaxes(tickprefix="$", tickformat=",.0f", title_text="Cuota (COP)",
                         rangemode="tozero", row=1, col=1)
        fig.update_yaxes(tickprefix="$", tickformat=",.0f", title_text="Acumulado (COP)",
                         rangemode="tozero", row=2, col=1)
        fig.update_xaxes(title_text="", row=1, col=1)
        fig.update_xaxes(title_text="Periodo", row=2, col=1)
        fig.update_layout(height=560, showlegend=False)
        show_plot(fig)

        with st.expander("Ver tabla de flujos"):
            df = pd.DataFrame({
                "Periodo": periodos_g,
                "Cuota ($)": flujos,
                "Incremento ($)": [0.0] + [flujos[k] - flujos[k - 1] for k in range(1, len(flujos))],
                "Incremento (%)": [0.0] + [(flujos[k] / flujos[k - 1] - 1) * 100 for k in range(1, len(flujos))],
                "Valor presente de la cuota ($)": [f / (1 + i_g) ** k for f, k in zip(flujos, periodos_g)],
            })
            show_table(df, column_config={
                "Cuota ($)": st.column_config.NumberColumn(format="$%.2f"),
                "Incremento ($)": st.column_config.NumberColumn(format="$%.2f"),
                "Incremento (%)": st.column_config.NumberColumn(format="%.2f%%"),
                "Valor presente de la cuota ($)": st.column_config.NumberColumn(format="$%.2f"),
            })

# ---------------------------------------------------------------------------
# 3) SUPUESTOS Y VERIFICACIÓN
# ---------------------------------------------------------------------------
with tab_ver:
    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        with st.container(border=True):
            section("Supuestos")
            st.markdown(
                "- **Tasa:** periódica efectiva, con la misma unidad de tiempo que los periodos.\n"
                "- **Serie vencida:** el pago cae al final de cada periodo.\n"
                "- **Serie anticipada:** el pago cae al inicio de cada periodo.\n"
                "- **Gradientes:** flujos vencidos; la primera cuota cae al final del periodo 1.\n"
                "- **Cuota uniforme equivalente:** serie vencida con el mismo valor presente."
            )
    with col_b:
        with st.container(border=True):
            section("Fórmulas empleadas")
            st.latex(r"VP=A\,\frac{1-(1+i)^{-n}}{i}\qquad VF=A\,\frac{(1+i)^n-1}{i}")
            st.latex(r"\text{anticipada}=\text{vencida}\cdot(1+i)")
            st.latex(r"VP_{G}=A_1\,a_{n,i}+\frac{G}{i}\left(a_{n,i}-\frac{n}{(1+i)^n}\right)")
            st.latex(r"VP_{g}=A_1\,\frac{1-\left(\frac{1+g}{1+i}\right)^n}{i-g}")

    st.write("")
    section("Verificación contra cálculo manual", "Se usan los parámetros de las pestañas anteriores.")
    desfase = 0 if not ant else -1
    vp_manual = sum(cuota_s / (1 + i_s) ** (k + desfase) for k in range(1, int(n_s) + 1))
    vf_manual = sum(cuota_s * (1 + i_s) ** (int(n_s) - k - desfase) for k in range(1, int(n_s) + 1))
    vp_grad_formula = (vp_gradiente_aritmetico_formula(a1, grad, n_g, i_g) if tipo_g == "Aritmético"
                       else vp_gradiente_geometrico_formula(a1, grad, n_g, i_g))
    filas = [
        ("Serie: VP = Σ cuota/(1+i)^k", vp_s, vp_manual),
        ("Serie: VF = Σ cuota·(1+i)^(n−k)", vf_s, vf_manual),
        ("Serie: cuota ida y vuelta (VP → cuota)", cuota_desde_vp(vp_s, i_s, n_s, ant), cuota_s),
        ("Serie anticipada = vencida · (1+i)", vp_serie(cuota_s, i_s, n_s, True),
         vp_serie(cuota_s, i_s, n_s, False) * (1 + i_s)),
        (f"Gradiente {tipo_g.lower()}: VP flujo a flujo = VP por fórmula", vp_g, vp_grad_formula),
        ("Gradiente: cuota equivalente · a(n,i) = VP", cuota_eq * factor_vp_serie(i_g, n_g), vp_g),
        ("Gradiente: VF = VP · (1+i)^n", vf_g, vp_g * (1 + i_g) ** n_g),
    ]
    verification_table(filas)
