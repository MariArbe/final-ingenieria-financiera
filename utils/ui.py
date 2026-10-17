"""Tema visual y componentes reutilizables para todo el tablero."""
import pandas as pd
import streamlit as st

# Paleta (estilo dashboard rosado: fondo suave, tarjetas blancas, acentos magenta)
WINE = "#8C1450"        # serie principal y tarjeta destacada
ROSE = "#E2337A"        # acento vivo
BLUSH = "#F5B3CC"       # barras y series secundarias claras
STONE = "#C9A3B6"       # serie de comparación (malva apagado)
INK = "#1E1A1D"         # títulos y texto principal
MUTED = "#8A717D"       # texto secundario
PINK = "#D6336C"        # etiquetas, ejes y cifras de las tarjetas
GRID = "#F6E4EC"
WINE_FILL = "rgba(140,20,80,0.08)"   # área bajo la curva principal

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700;9..40,800&display=swap');

:root {
    --wine: #8C1450; --wine-2: #A8175E; --pink: #D6336C; --rose: #E2337A;
    --ink: #1E1A1D; --muted: #8A717D; --line: #F3DCE6; --card: #FFFFFF;
    --shadow: 0 12px 34px rgba(170, 30, 90, 0.07);
    --shadow-strong: 0 18px 36px rgba(140, 20, 80, 0.32);
}

.stApp, .stApp p, .stApp label, .stApp li, .stApp input, .stApp textarea,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp button, .stApp td, .stApp th,
.stApp [data-testid="stCaptionContainer"], .stApp [data-baseweb="select"] div {
    font-family: 'DM Sans', 'Segoe UI', sans-serif;
}
.stApp {
    background: radial-gradient(1200px 600px at 85% -10%, #FFFFFF 0%, rgba(255,255,255,0) 60%),
                linear-gradient(180deg, #FDF0F5 0%, #FDF5F8 100%);
    color: var(--ink);
}
.block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1280px; }
header[data-testid="stHeader"] { background: transparent; }
.stApp [data-testid="stCaptionContainer"] { color: var(--muted); }

/* Barra lateral */
section[data-testid="stSidebar"] {
    background: #FFFFFF; border-right: none; box-shadow: 6px 0 30px rgba(170, 30, 90, 0.05);
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
    border-radius: 12px; margin: 2px 0; padding: 8px 12px; position: relative;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] span { color: #6E5A64; font-weight: 500; }
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover { background: #FDF0F5; }
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] { background: #FCE7EF; }
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] span {
    color: var(--wine); font-weight: 700;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"]::before {
    content: ""; position: absolute; left: -16px; top: 6px; bottom: 6px; width: 4px;
    border-radius: 0 4px 4px 0; background: var(--wine);
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] { border-color: var(--line); }
.side-brand { display: flex; align-items: center; gap: 10px; margin: 4px 0 6px 0; }
.side-heart { font-size: 1.7rem; line-height: 1;
              background: linear-gradient(160deg, #FF5C93 0%, #D6336C 100%);
              -webkit-background-clip: text; background-clip: text; color: transparent; }
.side-title { font-weight: 800; font-size: 1.05rem; color: var(--wine); letter-spacing: -0.01em; }
.side-sub { font-size: .8rem; color: var(--muted); margin-bottom: .6rem; }

/* Encabezado de página */
.page-head { margin: 0 0 26px 0; }
.page-head h1 { color: var(--ink); font-size: 2.5rem; font-weight: 800; margin: 0 0 6px 0;
                padding: 0; letter-spacing: -0.03em; line-height: 1.1; }
.page-head p { color: var(--muted); margin: 0; max-width: 80ch; font-size: 1rem; line-height: 1.55; }

/* Secciones */
.sec-title { font-weight: 700; font-size: 1.35rem; color: var(--ink); margin: 6px 0 2px 0;
             letter-spacing: -0.02em; }
.sec-caption { font-size: .88rem; color: var(--muted); margin-bottom: 12px; }

/* Tarjetas KPI */
.kpi { background: var(--card); border: none; border-radius: 18px; padding: 20px 20px;
       height: 100%; box-shadow: var(--shadow); container-type: inline-size; }
.kpi { padding-left: 18px; padding-right: 18px; }
.kpi-label { font-size: .95rem; color: var(--pink); font-weight: 500; }
/* La cifra se escala con el ancho de la tarjeta (cqi) para no partir los números */
.kpi-value { font-size: clamp(1rem, 14cqi, 2rem); font-weight: 700; color: var(--pink);
             margin-top: 8px; letter-spacing: -0.02em; font-variant-numeric: tabular-nums;
             line-height: 1.15; white-space: nowrap; }
.kpi-note { font-size: .8rem; color: var(--muted); margin-top: 10px; }
.kpi-accent { background: linear-gradient(150deg, #7A0B42 0%, #9C1157 100%);
              box-shadow: var(--shadow-strong); }
.kpi-accent .kpi-label { color: #FFE4EE; }
.kpi-accent .kpi-value { color: #FFFFFF; }
.kpi-accent .kpi-note { color: #F9C9DA; }

/* Avisos */
.callout { border-radius: 14px; padding: 13px 18px; font-size: .93rem; line-height: 1.55; margin: 12px 0;
           border: none; }
.callout-info { background: #FFFFFF; color: #5E1238; box-shadow: var(--shadow);
                border-left: 4px solid var(--pink); }
.callout-ok   { background: #F1FBF4; color: #14532D; border-left: 4px solid #22A35A; }
.callout-warn { background: #FFF8EB; color: #78350F; border-left: 4px solid #E0A526; }

/* Pestañas */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] { padding: 10px 16px; }
.stTabs [data-baseweb="tab"] p { font-weight: 600; color: var(--muted); }
.stTabs [aria-selected="true"] p { color: var(--wine); }
.stTabs [data-baseweb="tab-highlight"] { background-color: var(--wine); height: 3px; border-radius: 3px; }
.stTabs [data-baseweb="tab-border"] { display: none; }

/* Tarjetas (contenedores con borde) */
div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"],
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 20px; border: none !important; background: var(--card); box-shadow: var(--shadow);
    padding: 22px 22px 20px 22px;
}

/* Gráficos y tablas como tarjetas blancas */
div[data-testid="stPlotlyChart"] {
    background: var(--card); border-radius: 20px; padding: 14px 16px 8px 16px; box-shadow: var(--shadow);
}
div[data-testid="stDataFrame"], div[data-testid="stTable"] {
    background: var(--card); border-radius: 14px; box-shadow: var(--shadow); overflow: hidden;
}

/* Campos de entrada */
.stApp label p { color: #5B4A53; font-weight: 500; }
div[data-baseweb="select"] > div, div[data-baseweb="input"] {
    background: #FCF2F6 !important; border-radius: 12px !important;
    border: 1px solid var(--line) !important;
}
div[data-baseweb="base-input"], div[data-baseweb="input"] input { background: transparent !important; }
[data-testid="stNumberInputContainer"], [data-testid="stTextInputRootElement"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div, [data-testid="stDateInput"] [data-baseweb="input"] {
    border: 1px solid var(--line) !important; border-radius: 12px !important;
}
div[data-baseweb="select"] > div div { color: var(--pink); }
.stNumberInput button { background: transparent; color: var(--pink); }
.stNumberInput button:hover { background: #FDF0F5; color: var(--wine); }

/* Desplegables */
div[data-testid="stExpander"] details {
    border: none; border-radius: 18px; background: var(--card); box-shadow: var(--shadow);
}
div[data-testid="stExpander"] summary p { font-weight: 600; color: var(--ink); }

/* Botones: blancos con borde y texto rosado */
.stButton > button, .stDownloadButton > button, a[data-testid="stPageLink-NavLink"] {
    border-radius: 12px; font-weight: 600; background: #FFFFFF; color: var(--pink);
    border: 1px solid #F1CFDD;
}
.stButton > button:hover, .stDownloadButton > button:hover { border-color: var(--pink); color: var(--wine);
                                                             background: #FFF7FA; }
a[data-testid="stPageLink-NavLink"] { display: inline-flex; padding: 4px 12px; margin-top: 4px; }
a[data-testid="stPageLink-NavLink"] p { color: var(--pink); font-weight: 600; }
a[data-testid="stPageLink-NavLink"]:hover { background: #FFF7FA; border-color: var(--pink); }
"""


def setup_page(title, icon="💎"):
    """Debe llamarse primero en cada página."""
    st.set_page_config(
        page_title=f"{title} | Ingeniería Financiera UPB",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)
    with st.sidebar:
        st.markdown(
            '<div class="side-brand"><span class="side-heart">&#10084;</span>'
            '<span class="side-title">Ingeniería Financiera</span></div>'
            '<div class="side-sub">Universidad Pontificia Bolivariana</div>',
            unsafe_allow_html=True,
        )
        st.caption("Docente: Adriana Arango L.")
        st.caption("Entrega: jueves 29 de octubre de 2026")


def _h(text):
    # El símbolo $ activa LaTeX en el markdown de Streamlit; se escapa como entidad.
    return str(text).replace("$", "&#36;")


def page_header(title, subtitle):
    st.markdown(
        f'<div class="page-head"><h1>{_h(title)}</h1><p>{_h(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def section(title, caption=None):
    html = f'<div class="sec-title">{_h(title)}</div>'
    if caption:
        html += f'<div class="sec-caption">{_h(caption)}</div>'
    st.markdown(html, unsafe_allow_html=True)


def kpi(label, value, note=None, accent=False):
    cls = "kpi kpi-accent" if accent else "kpi"
    note_html = f'<div class="kpi-note">{_h(note)}</div>' if note else ""
    # Cifras cortas se ven grandes; las largas se reducen para caber en una línea
    tam = 180 / max(len(str(value)), 6)
    st.markdown(
        f'<div class="{cls}"><div class="kpi-label">{_h(label)}</div>'
        f'<div class="kpi-value" style="font-size: clamp(1rem, {tam:.1f}cqi, 2.1rem)">{_h(value)}</div>'
        f'{note_html}</div>',
        unsafe_allow_html=True,
    )


def callout(text, kind="info"):
    st.markdown(f'<div class="callout callout-{kind}">{_h(text)}</div>', unsafe_allow_html=True)


def money(x, decimals=0):
    return f"${x:,.{decimals}f}"


def pct(x, decimals=4):
    return f"{x * 100:.{decimals}f}%"


def style_fig(fig, title, xtitle, ytitle):
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=17, color=INK), x=0, xanchor="left"),
        xaxis_title=xtitle,
        yaxis_title=ytitle,
        template="simple_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, Segoe UI, sans-serif", color=PINK, size=13),
        margin=dict(l=10, r=10, t=64, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1, title=None,
                    font=dict(color=INK)),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#F1CFDD", font=dict(color=INK)),
        height=380,
        bargap=0.25,
    )
    try:
        fig.update_layout(barcornerradius=6)
    except Exception:
        pass  # versiones antiguas de Plotly no tienen esquinas redondeadas
    fig.update_xaxes(showgrid=False, showline=True, linecolor=GRID, ticks="",
                     tickfont=dict(color=PINK), title_font=dict(color=MUTED))
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, showline=False, ticks="",
                     tickfont=dict(color=PINK), title_font=dict(color=MUTED))
    return fig


def show_plot(fig):
    try:
        st.plotly_chart(fig, width="stretch")
    except Exception:
        st.plotly_chart(fig, use_container_width=True)


def show_table(df, **kwargs):
    try:
        st.dataframe(df, width="stretch", hide_index=True, **kwargs)
    except Exception:
        st.dataframe(df, use_container_width=True, hide_index=True, **kwargs)


def verification_table(rows, tol=1e-6):
    """rows: lista de (nombre, resultado_del_modulo, calculo_manual[, escala]).

    La tolerancia es relativa: tol × max(1, |manual|, escala). La `escala` opcional
    sirve cuando el valor esperado es 0 (p. ej. saldo final de un crédito): sin ella
    la tolerancia quedaría absoluta (1e-6) y el error de redondeo acumulado en
    cientos de periodos sobre un capital grande la superaría sin que haya error real.
    """
    data, todo_ok = [], True
    for fila in rows:
        nombre, modelo, manual = fila[:3]
        escala = abs(fila[3]) if len(fila) > 3 else 0.0
        diff = abs(modelo - manual)
        ok = diff <= tol * max(1.0, abs(manual), escala)
        todo_ok = todo_ok and ok
        data.append({
            "Prueba": nombre,
            "Resultado del módulo": f"{modelo:,.6f}",
            "Cálculo manual": f"{manual:,.6f}",
            "Diferencia": f"{diff:.2e}",
            "Estado": "✅ Coincide" if ok else "❌ Revisar",
        })
    show_table(pd.DataFrame(data))
    if todo_ok:
        callout("Todas las verificaciones coinciden con el cálculo manual.", "ok")
    else:
        callout("Hay diferencias entre el módulo y el cálculo manual: revisa las fórmulas.", "warn")
    return todo_ok


def safe_page_link(path, label, icon=None):
    try:
        st.page_link(path, label=label, icon=icon)
    except Exception:
        st.caption("Disponible próximamente")