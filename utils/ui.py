"""Tema visual y componentes reutilizables para todo el tablero."""
import html as _html
import re

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

# Corazón en SVG (nítido a cualquier tamaño y toma el color del texto)
HEART = ('<svg class="hrt" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21.2s-7.6-4.7-10.1-9.5'
         'C.3 8.4 2.2 4.2 6.2 3.8c2.2-.2 4 .9 5.8 3.1 1.8-2.2 3.6-3.3 5.8-3.1 4 .4 5.9 4.6 4.3 7.9'
         'C19.6 16.5 12 21.2 12 21.2z"/></svg>')

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
/* La página principal se llama app.py (lo exige el despliegue); en el menú se muestra "Sobre la app" */
section[data-testid="stSidebar"] span[label="app"] p { font-size: 0; }
section[data-testid="stSidebar"] span[label="app"] p::after { content: "Sobre la app"; font-size: 0.875rem; }
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

/* ---------- Corazones ---------- */
.hrt { width: .78em; height: .78em; fill: currentColor; display: inline-block;
       vertical-align: -0.06em; flex: none; }
.page-head h1 .hrt { width: .38em; height: .38em; color: var(--rose); margin-left: .16em;
                     vertical-align: .62em; }
.sec-title { display: flex; align-items: flex-start; gap: 8px; }
.sec-title .hrt { width: .6em; height: .6em; color: var(--rose); margin-top: .42em; }
.side-heart .hrt { width: 1.45rem; height: 1.45rem; color: var(--rose); }
.side-heart { background: none; -webkit-background-clip: initial; background-clip: initial; }
.kpi-accent { position: relative; overflow: hidden; }
.kpi-accent .kpi-heart { position: absolute; right: -14px; bottom: -22px; color: #FFFFFF;
                         opacity: .10; pointer-events: none; }
.kpi-accent .kpi-heart .hrt { width: 104px; height: 104px; }
.kpi-accent > div:not(.kpi-heart) { position: relative; }

/* ---------- Distribución equilibrada ---------- */
/* Menos separación entre columnas: el contenido gana ancho y la página se ve pareja */
div[data-testid="stHorizontalBlock"] { gap: 1.25rem !important; }
/* Filas "hoja" (sin columnas anidadas): todas las tarjetas de la fila con la misma altura */
div[data-testid="stHorizontalBlock"]:not(:has(div[data-testid="stHorizontalBlock"])) {
    align-items: stretch !important;
}
div[data-testid="stHorizontalBlock"]:not(:has(div[data-testid="stHorizontalBlock"]))
    > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] { height: 100%; }
div[data-testid="stHorizontalBlock"]:not(:has(div[data-testid="stHorizontalBlock"]))
    > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]
    > div[data-testid="stLayoutWrapper"]:only-child { flex: 1 1 auto; }
div[data-testid="stHorizontalBlock"]:not(:has(div[data-testid="stHorizontalBlock"]))
    > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]
    > div[data-testid="stLayoutWrapper"]:only-child > div[data-testid="stVerticalBlock"] { height: 100%; }
/* Tarjetas KPI de una fila: misma altura, nota abajo */
div[data-testid="stElementContainer"]:only-child:has(.kpi) { flex: 1 1 auto; }
div[data-testid="stElementContainer"]:only-child:has(.kpi) [data-testid="stMarkdown"],
div[data-testid="stElementContainer"]:only-child:has(.kpi) [data-testid="stMarkdown"] > div,
div[data-testid="stElementContainer"]:only-child:has(.kpi) [data-testid="stMarkdownContainer"] { height: 100%; }
.kpi { display: flex; flex-direction: column; }
.kpi-note { margin-top: auto; padding-top: 10px; }
/* Las tarjetas de módulos alinean el botón abajo */
div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]
    > div[data-testid="stElementContainer"]:has(a[data-testid="stPageLink-NavLink"]) { margin-top: auto; }
/* Fórmulas: nunca se cortan; si no caben, se desplazan dentro de la tarjeta */
.stApp .katex-display { overflow-x: auto; overflow-y: hidden; padding: 2px 0; margin: .55em 0; }
.stApp .katex-display { scrollbar-width: none; }
.stApp .katex-display::-webkit-scrollbar { display: none; }
.stApp .katex-display > .katex { font-size: 1.03em; }

/* ---------- Tablas con la estética de los gráficos ---------- */
.tbl-card { background: var(--card); border-radius: 20px; box-shadow: var(--shadow);
            padding: 6px 8px 8px 8px; margin: 2px 0 14px 0; }
.tbl-scroll { overflow: auto; max-height: var(--tbl-max, none); border-radius: 14px; }
.tbl { width: 100%; border-collapse: separate; border-spacing: 0; font-size: .88rem; margin: 0;
       font-variant-numeric: tabular-nums; }
.stApp .tbl th, .stApp .tbl td { border: none; }
.tbl thead th { position: sticky; top: 0; z-index: 1; background: #FFFFFF; text-align: left;
                color: var(--pink); font-weight: 600; font-size: .8rem; padding: 12px 10px 10px 10px;
                border-bottom: 2px solid var(--line) !important; vertical-align: bottom; line-height: 1.3; }
.tbl tbody td { padding: 10px 10px; color: #3F3239; border-bottom: 1px solid #FAEEF3 !important;
                vertical-align: top; }
.tbl tbody tr:last-child td { border-bottom: none; }
.tbl tbody tr:hover td { background: #FFF6FA; }
.tbl td.num, .tbl th.num { text-align: right; }
.tbl td.num, .tbl td.nw { white-space: nowrap; }
.tbl td:first-child { color: var(--ink); font-weight: 500; }
.tbl .pill { display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px;
             border-radius: 999px; font-size: .8rem; font-weight: 600; white-space: nowrap; }
.tbl .pill-ok { background: #FCE7EF; color: var(--wine); }
.tbl .pill-ok .hrt { color: var(--rose); }
.tbl .pill-bad { background: #FFF1D6; color: #8A4B08; }

/* Tarjetas de resumen por módulo (panel principal) */
.mod-head { display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 1rem; color: var(--ink); }
.mod-value { font-size: 1.85rem; font-weight: 700; color: var(--pink); letter-spacing: -0.02em;
             font-variant-numeric: tabular-nums; line-height: 1.15; margin-top: 8px; }
.mod-what { font-size: .8rem; color: var(--pink); font-weight: 500; margin-top: 2px; }
.mod-note { font-size: .84rem; color: var(--muted); line-height: 1.5; margin-top: 8px; }
/* El minigráfico de una tarjeta de módulo (key "modcard_…") no lleva su propia tarjeta */
[class*="st-key-modcard"] div[data-testid="stPlotlyChart"] {
    box-shadow: none; padding: 0; background: transparent; border-radius: 0;
}

/* Estado vacío */
.empty { background: var(--card); border-radius: 20px; box-shadow: var(--shadow); text-align: center;
         padding: 54px 28px 50px 28px; margin: 4px 0 12px 0; }
.empty .empty-heart { display: inline-flex; align-items: center; justify-content: center; width: 72px;
                      height: 72px; border-radius: 50%; background: #FCE7EF; color: var(--rose);
                      margin-bottom: 16px; }
.empty .empty-heart .hrt { width: 32px; height: 32px; }
.empty h3 { font-size: 1.2rem; font-weight: 700; color: var(--ink); margin: 0 0 6px 0; padding: 0; }
.empty p { color: var(--muted); margin: 0 auto; max-width: 52ch; font-size: .93rem; line-height: 1.55; }
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
            f'<div class="side-brand"><span class="side-heart">{HEART}</span>'
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
        f'<div class="page-head"><h1>{_h(title)}{HEART}</h1><p>{_h(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def section(title, caption=None):
    html = f'<div class="sec-title">{HEART}<span>{_h(title)}</span></div>'
    if caption:
        html += f'<div class="sec-caption">{_h(caption)}</div>'
    st.markdown(html, unsafe_allow_html=True)


def kpi(label, value, note=None, accent=False):
    cls = "kpi kpi-accent" if accent else "kpi"
    note_html = f'<div class="kpi-note">{_h(note)}</div>' if note else ""
    # Cifras cortas se ven grandes; las largas se reducen para caber en una línea
    tam = 180 / max(len(str(value)), 6)
    marca = f'<div class="kpi-heart">{HEART}</div>' if accent else ""
    st.markdown(
        f'<div class="{cls}">{marca}<div class="kpi-label">{_h(label)}</div>'
        f'<div class="kpi-value" style="font-size: clamp(1rem, {tam:.1f}cqi, 2.1rem)">{_h(value)}</div>'
        f'{note_html}</div>',
        unsafe_allow_html=True,
    )


def callout(text, kind="info"):
    st.markdown(f'<div class="callout callout-{kind}">{_h(text)}</div>', unsafe_allow_html=True)


def resumen_modulo(icono, nombre, valor, que_es, nota):
    """Encabezado de una tarjeta de resumen: módulo, cifra clave, qué es esa cifra y una frase."""
    st.markdown(
        f'<div class="mod-head"><span>{icono}</span><span>{_h(nombre)}</span></div>'
        f'<div class="mod-value">{_h(valor)}</div><div class="mod-what">{_h(que_es)}</div>'
        f'<div class="mod-note">{_h(nota)}</div>',
        unsafe_allow_html=True,
    )


def mini_fig(fig, height=150, etiquetas_x=False):
    """Gráfico pequeño para una tarjeta: sin título, ejes discretos, sin leyenda.
    `etiquetas_x=True` muestra los nombres del eje x (para barras por categoría)."""
    fig.update_layout(
        template="simple_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=height, margin=dict(l=4, r=4, t=8, b=4), showlegend=False, hovermode="x unified",
        font=dict(family="DM Sans, Segoe UI, sans-serif", color=MUTED, size=10.5),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#F1CFDD", font=dict(color=INK)),
        bargap=0.25,
    )
    try:
        fig.update_layout(barcornerradius=4)
    except Exception:
        pass
    fig.update_xaxes(showgrid=False, showline=True, linecolor=GRID, ticks="", showticklabels=etiquetas_x,
                     tickfont=dict(color=MUTED, size=10))
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, showline=False, ticks="",
                     tickfont=dict(color=MUTED, size=10), nticks=3)
    try:
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    except Exception:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def empty_state(title, text):
    """Tarjeta centrada para cuando una sección aún no tiene datos."""
    st.markdown(
        f'<div class="empty"><div class="empty-heart">{HEART}</div><h3>{_h(title)}</h3>'
        f'<p>{_h(text)}</p></div>',
        unsafe_allow_html=True,
    )


def money(x, decimals=0):
    # Negativos como -$150,000 (no $-150,000)
    return f"-${abs(x):,.{decimals}f}" if x < 0 and round(abs(x), decimals) > 0 else f"${abs(x):,.{decimals}f}"


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


_NUM_TXT = re.compile(r"^[\s$−\-+(]*[\d.,]+[\d.,e+\-%)\s]*$")


def _formato(fmt, v):
    """Aplica los formatos de st.column_config.NumberColumn que usa el tablero."""
    if fmt == "percent":
        return f"{v * 100:,.4f}%"
    if fmt in ("%d", "%i"):
        return f"{int(round(v)):,}"
    m = re.fullmatch(r"(.*)%(,?)\.(\d+)f(.*)", fmt or "")
    if m:
        pre, _, dec, post = m.groups()
        pre, post = pre.replace("%%", "%"), post.replace("%%", "%")   # "%.2f%%" -> 1.00%
        dec = int(dec)
        if round(v, dec) == 0:
            v = 0.0                                   # evita "-0.00" por residuos de redondeo
        signo = "-" if v < 0 else ""
        return f"{signo}{pre}{abs(v):,.{dec}f}{post}"   # -$1,000.00 y no $-1,000.00
    return f"{0.0 if round(v, 2) == 0 else v:,.2f}"


def _celda(valor, fmt):
    """Devuelve (html, es_numero) para una celda."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return "", False
    if isinstance(valor, str):
        if valor.startswith("✅"):
            return f'<span class="pill pill-ok">{HEART}{_h(_html.escape(valor[1:].strip()))}</span>', False
        if valor.startswith("❌"):
            return f'<span class="pill pill-bad">{_h(_html.escape(valor[1:].strip()))}</span>', False
        return _h(_html.escape(valor)), bool(_NUM_TXT.match(valor))
    if isinstance(valor, bool):
        return ("Sí" if valor else "No"), False
    if isinstance(valor, int) or (hasattr(valor, "dtype") and pd.api.types.is_integer(valor)):
        return _h(_formato(fmt, valor) if fmt else f"{int(valor):,}"), True
    if isinstance(valor, float) or pd.api.types.is_number(valor):
        return _h(_formato(fmt, float(valor))), True
    return _h(_html.escape(str(valor))), False


def show_table(df, column_config=None, max_rows_visible=12, **_):
    """Tabla con la misma estética de los gráficos: tarjeta blanca, encabezado rosado,
    cifras alineadas y encabezado fijo cuando la tabla es larga."""
    formatos = {}
    for col, cfg in (column_config or {}).items():
        tc = (cfg or {}).get("type_config") or {}
        if tc.get("format"):
            formatos[col] = tc["format"]

    cols = list(df.columns)
    numericas = {c: pd.api.types.is_numeric_dtype(df[c]) for c in cols}
    filas_html = []
    num_txt = {c: True for c in cols}
    for fila in df.itertuples(index=False, name=None):
        celdas = []
        for c, v in zip(cols, fila):
            contenido, es_num = _celda(v, formatos.get(c))
            num_txt[c] = num_txt[c] and (es_num or contenido == "")
            celdas.append((c, contenido, es_num))
        filas_html.append(celdas)

    cortas = {c: (not numericas[c]) and len(df) > 0 and
                 max(len(str(v)) for v in df[c].tolist()) <= 24 for c in cols}

    def clase(c):
        if numericas[c] or (num_txt[c] and len(df)):
            return ' class="num"'
        return ' class="nw"' if cortas[c] else ""

    head = "".join(f"<th{clase(c)}>{_h(_html.escape(str(c)))}</th>" for c in cols)
    body = "".join(
        "<tr>" + "".join(f"<td{clase(c)}>{contenido}</td>" for c, contenido, _ in celdas) + "</tr>"
        for celdas in filas_html
    )
    alto = f' style="--tbl-max: {44 * max_rows_visible + 46}px"' if len(df) > max_rows_visible else ""
    st.markdown(
        f'<div class="tbl-card"><div class="tbl-scroll"{alto}><table class="tbl">'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></div>",
        unsafe_allow_html=True,
    )


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
        # Residuos de redondeo como -0.00000002 se muestran como 0 (no como "-0.000000")
        ver = lambda x: 0.0 if abs(x) < 5e-7 else x
        data.append({
            "Prueba": nombre,
            "Resultado del módulo": f"{ver(modelo):,.6f}",
            "Cálculo manual": f"{ver(manual):,.6f}",
            "Diferencia": f"{diff:.2e}",
            "Estado": "✅ Coincide" if ok else "❌ Revisar",
        })
    show_table(pd.DataFrame(data), max_rows_visible=40)
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