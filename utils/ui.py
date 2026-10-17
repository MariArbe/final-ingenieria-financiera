"""Tema visual y componentes reutilizables para todo el tablero."""
import pandas as pd
import streamlit as st

# Paleta
WINE = "#881337"
ROSE = "#E11D48"
BLUSH = "#FDA4AF"
STONE = "#A8A29E"
INK = "#292524"
MUTED = "#78716C"
GRID = "#EEE7E5"

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

.stApp, .stApp p, .stApp label, .stApp li, .stApp input, .stApp textarea,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp button,
.stApp [data-testid="stCaptionContainer"] {
    font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
}
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1240px; }
header[data-testid="stHeader"] { background: transparent; }

/* Sidebar */
section[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #EADFDD; }
.side-title { font-weight: 800; font-size: 1.05rem; color: #881337; letter-spacing: -0.01em; }
.side-sub { font-size: .82rem; color: #78716C; margin-bottom: .6rem; }

/* Hero */
.hero { background: linear-gradient(120deg, #7F1236 0%, #B3123F 100%);
        border-radius: 18px; padding: 28px 34px; margin-bottom: 22px; }
.hero h1 { color: #fff; font-size: 2rem; font-weight: 800; margin: 0 0 6px 0;
           padding: 0; letter-spacing: -0.02em; line-height: 1.15; }
.hero p { color: #FCE7EB; margin: 0; max-width: 72ch; font-size: 1rem; line-height: 1.55; }

/* Secciones */
.sec-title { font-weight: 700; font-size: 1.05rem; color: #292524; margin: 2px 0 2px 0; }
.sec-caption { font-size: .85rem; color: #78716C; margin-bottom: 10px; }

/* KPIs */
.kpi { background: #fff; border: 1px solid #EADFDD; border-radius: 14px;
       padding: 16px 18px; height: 100%; }
.kpi-label { font-size: .82rem; color: #78716C; font-weight: 600; }
.kpi-value { font-size: 1.5rem; font-weight: 800; color: #292524; margin-top: 2px;
             letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }
.kpi-note { font-size: .8rem; color: #78716C; margin-top: 2px; }
.kpi-accent { background: #881337; border-color: #881337; }
.kpi-accent .kpi-label, .kpi-accent .kpi-note { color: #FBCFD8; }
.kpi-accent .kpi-value { color: #fff; }

/* Avisos */
.callout { border-radius: 12px; padding: 12px 16px; font-size: .93rem; line-height: 1.5; margin: 10px 0; }
.callout-info { background: #FFF1F2; border: 1px solid #FECDD3; color: #4C0519; }
.callout-ok   { background: #F0FDF4; border: 1px solid #BBF7D0; color: #14532D; }
.callout-warn { background: #FFFBEB; border: 1px solid #FDE68A; color: #78350F; }

/* Pestañas */
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #EADFDD; }
.stTabs [data-baseweb="tab"] { padding: 10px 16px; font-weight: 600; color: #78716C; }
.stTabs [aria-selected="true"] { color: #881337; }
.stTabs [data-baseweb="tab-highlight"] { background-color: #881337; }

/* Contenedores con borde */
div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 14px; border-color: #EADFDD; background: #FFFFFF; }
.stButton > button, .stDownloadButton > button { border-radius: 10px; font-weight: 600; }
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
            '<div class="side-title">Ingeniería Financiera</div>'
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
        f'<div class="hero"><h1>{_h(title)}</h1><p>{_h(subtitle)}</p></div>',
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
    st.markdown(
        f'<div class="{cls}"><div class="kpi-label">{_h(label)}</div>'
        f'<div class="kpi-value">{_h(value)}</div>{note_html}</div>',
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
        title=dict(text=title, font=dict(size=16, color=INK), x=0, xanchor="left"),
        xaxis_title=xtitle,
        yaxis_title=ytitle,
        template="simple_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, Segoe UI, sans-serif", color=INK, size=13),
        margin=dict(l=10, r=10, t=60, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1, title=None),
        hovermode="x unified",
        height=380,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
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