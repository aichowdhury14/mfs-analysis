"""Shared visual theme: CSS injection, Plotly template, and reusable UI components.

Keeping this in one place means every page looks consistent without copy-pasting
markup, and a palette change only happens in one file.
"""
from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

COLORS = {
    "accent": "#0C8A68",
    "accent_light": "#E4F2EC",
    "amber": "#C7752A",
    "blue": "#3D6FC4",
    "rose": "#B23A6B",
    "ink": "#16211D",
    "ink_soft": "#3A473F",
    "muted": "#5C6B64",
    "line": "#DDD8C9",
    "paper": "#F7F5EF",
    "card": "#FFFFFF",
    "good": "#0C8A68",
    "bad": "#B23A2A",
}

CATEGORY_PALETTE = ["#0C8A68", "#C7752A", "#3D6FC4", "#B23A6B", "#8B8F5A", "#6B8FA8", "#A87B4F", "#7A6B9C", "#9B9B8F"]


def inject_css() -> None:
    st.markdown(
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,500;6..72,600;6..72,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap">',
        unsafe_allow_html=True,
    )
    css = f"""
html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', system-ui, sans-serif;
}}
h1, h2, h3 {{
    font-family: 'Newsreader', serif !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em;
}}
.block-container {{
    padding-top: 2rem;
    max-width: 1200px;
}}
.page-eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: {COLORS['accent']};
    margin-bottom: 0.2rem;
}}
.page-caption {{
    color: {COLORS['muted']};
    font-size: 0.95rem;
    max-width: 640px;
    margin-top: -0.3rem;
}}
div[data-testid="stMetric"] {{
    background: {COLORS['card']};
    border: 1px solid {COLORS['line']};
    border-radius: 12px;
    padding: 1rem 1.2rem 0.9rem;
    box-shadow: 0 1px 2px rgba(22,33,29,0.04), 0 4px 14px rgba(22,33,29,0.04);
}}
div[data-testid="stMetricLabel"] {{
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: {COLORS['muted']} !important;
}}
div[data-testid="stMetricValue"] {{
    font-family: 'Newsreader', serif !important;
    font-weight: 600 !important;
}}
button[data-baseweb="tab"] {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 500;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {COLORS['accent']} !important;
}}
div[data-baseweb="tab-highlight"] {{
    background-color: {COLORS['accent']} !important;
}}
div[data-testid="stDataFrame"] {{
    border: 1px solid {COLORS['line']};
    border-radius: 10px;
}}
section[data-testid="stSidebar"] {{
    border-right: 1px solid {COLORS['line']};
}}
.sidebar-brand {{
    font-family: 'Newsreader', serif;
    font-weight: 600;
    font-size: 1.25rem;
    color: {COLORS['ink']};
    padding: 0.4rem 0 0.1rem;
}}
.sidebar-sub {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: {COLORS['muted']};
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid {COLORS['line']};
    margin-bottom: 0.6rem;
}}
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-radius: 5px;
    padding: 2px 8px;
    margin-left: 6px;
}}
.badge-estimate {{ color: {COLORS['amber']}; border: 1px solid {COLORS['amber']}; }}
.badge-official {{ color: {COLORS['good']}; border: 1px solid {COLORS['good']}; }}
.stMarkdown h2, .stMarkdown h3 {{ margin-top: 0.4rem; }}
"""
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def page_header(eyebrow: str, title: str, caption: str = "") -> None:
    st.markdown(f'<div class="page-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.markdown(f"## {title}")
    if caption:
        st.markdown(f'<div class="page-caption">{caption}</div>', unsafe_allow_html=True)
    st.write("")


def sidebar_brand() -> None:
    st.sidebar.markdown('<div class="sidebar-brand">📱 MFS Bangladesh</div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-sub">Payment Systems Analytics</div>', unsafe_allow_html=True)


def apply_plotly_template() -> None:
    """Register a consistent Plotly template used by every chart in the app."""
    template = go.layout.Template()
    template.layout = go.Layout(
        font=dict(family="IBM Plex Sans, sans-serif", color=COLORS["ink_soft"], size=13),
        title_font=dict(family="Newsreader, serif", size=17, color=COLORS["ink"]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=CATEGORY_PALETTE,
        xaxis=dict(gridcolor=COLORS["line"], zerolinecolor=COLORS["line"], showgrid=False),
        yaxis=dict(gridcolor=COLORS["line"], zerolinecolor=COLORS["line"], gridwidth=1),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=12)),
        margin=dict(l=10, r=10, t=40, b=10),
        hoverlabel=dict(font_family="IBM Plex Mono, monospace", font_size=12, bgcolor=COLORS["ink"], font_color=COLORS["paper"]),
    )
    pio.templates["mfs"] = template
    pio.templates.default = "mfs"


def style_fig(fig: go.Figure, height: int = 420, hovermode: str = "x unified") -> go.Figure:
    """Apply common sizing/hover behavior after a figure is built."""
    fig.update_layout(height=height, hovermode=hovermode)
    return fig
