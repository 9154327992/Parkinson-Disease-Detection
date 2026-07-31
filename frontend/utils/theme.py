"""
Theme utilities for the
Parkinson Disease Detection Agent.
"""

from pathlib import Path
import streamlit as st


# ==========================================================
# Theme Configuration
# ==========================================================

LIGHT_THEME = {
    "primary": "#2563EB",
    "secondary": "#10B981",
    "background": "#FFFFFF",
    "card": "#F8FAFC",
    "text": "#111827",
    "border": "#E5E7EB"
}

DARK_THEME = {
    "primary": "#3B82F6",
    "secondary": "#34D399",
    "background": "#0F172A",
    "card": "#1E293B",
    "text": "#F8FAFC",
    "border": "#334155"
}


# ==========================================================
# Load CSS
# ==========================================================

def load_css():

    css_path = (
        Path(__file__).parent.parent
        / "assets"
        / "style.css"
    )

    if css_path.exists():

        with open(css_path, "r", encoding="utf-8") as file:

            st.markdown(
                f"<style>{file.read()}</style>",
                unsafe_allow_html=True
            )


# ==========================================================
# Get Theme
# ==========================================================

def get_theme():

    return st.session_state.get(
        "theme",
        "Light"
    )


# ==========================================================
# Set Theme
# ==========================================================

def set_theme(theme):

    st.session_state["theme"] = theme


# ==========================================================
# Theme Colors
# ==========================================================

def theme_colors():

    if get_theme() == "Dark":

        return DARK_THEME

    return LIGHT_THEME


# ==========================================================
# Page Header
# ==========================================================

def page_header(
    title,
    subtitle=""
):

    colors = theme_colors()

    st.markdown(
        f"""
<div style="
padding:20px;
border-radius:12px;
background:{colors['card']};
border:1px solid {colors['border']};
margin-bottom:20px;
">

<h1 style="
margin:0;
color:{colors['primary']};
">
{title}
</h1>

<p style="
margin-top:8px;
color:{colors['text']};
">
{subtitle}
</p>

</div>
""",
        unsafe_allow_html=True
    )


# ==========================================================
# Section Header
# ==========================================================

def section_header(title):

    st.markdown(f"## {title}")


# ==========================================================
# Divider
# ==========================================================

def divider():

    st.markdown("---")


# ==========================================================
# Success Message
# ==========================================================

def success(message):

    st.success(message)


# ==========================================================
# Warning Message
# ==========================================================

def warning(message):

    st.warning(message)


# ==========================================================
# Error Message
# ==========================================================

def error(message):

    st.error(message)


# ==========================================================
# Info Message
# ==========================================================

def info(message):

    st.info(message)


# ==========================================================
# Apply Theme
# ==========================================================

def apply_theme():

    load_css()
