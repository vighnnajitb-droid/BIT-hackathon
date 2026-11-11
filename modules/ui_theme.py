"""
ui_theme.py
Custom CSS and visual components for Rajasthan Royals-inspired dark theme.
Colors:
- Midnight Navy: #090D18 / #0C1220
- Royal Pink: #E83E82 / #FF78AD / #BD367A
- Electric Cyan: #55D6E8 / #72E2EF
- Soft Gold / Amber: #F4C76B
- Clean Dark Panels: rgba(17, 24, 39, 0.85)
"""
import streamlit as st

def apply_custom_theme():
    """Injects high-end franchise CSS into Streamlit."""
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
  --navy-base: #070B14;
  --navy-surface: #0E1626;
  --navy-card: #131E33;
  --navy-card-hover: #192742;
  --rr-pink: #E83E82;
  --rr-pink-light: #FF78AD;
  --rr-pink-glow: rgba(232, 62, 130, 0.35);
  --cyan-accent: #55D6E8;
  --gold-accent: #F4C76B;
  --text-primary: #F8FAFC;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-accent: rgba(232, 62, 130, 0.3);
}

html, body, [class*="css"] {
  font-family: 'Plus Jakarta Sans', sans-serif;
  color: var(--text-primary);
}

.stApp {
  background:
    radial-gradient(circle at 90% 5%, rgba(232, 62, 130, 0.12) 0%, transparent 40%),
    radial-gradient(circle at 10% 85%, rgba(85, 214, 232, 0.08) 0%, transparent 40%),
    linear-gradient(160deg, #070B14 0%, #0A101D 50%, #080D18 100%);
  color: var(--text-primary);
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #090E1A 0%, #0B1324 100%);
  border-right: 1px solid var(--border-subtle);
}

[data-testid="stHeader"] {
  background: rgba(7, 11, 20, 0.85);
  backdrop-filter: blur(12px);
}

h1, h2, h3, h4 {
  font-family: 'Space Grotesk', sans-serif !important;
  letter-spacing: -0.025em;
  color: #FFFFFF;
}

/* Hero Branding Card */
.rr-hero-banner {
  position: relative;
  overflow: hidden;
  border-radius: 20px;
  border: 1px solid var(--border-accent);
  background: linear-gradient(125deg, rgba(232, 62, 130, 0.18) 0%, rgba(14, 22, 38, 0.95) 45%, rgba(85, 214, 232, 0.1) 100%);
  padding: 30px 34px;
  margin-bottom: 24px;
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
}

.rr-hero-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 34px;
  font-weight: 800;
  line-height: 1.15;
  color: #FFFFFF;
  margin: 6px 0 10px 0;
}

.rr-hero-subtitle {
  color: #CBD5E1;
  font-size: 14.5px;
  line-height: 1.5;
  max-width: 820px;
}

.rr-badge-pink {
  display: inline-flex;
  align-items: center;
  background: rgba(232, 62, 130, 0.15);
  border: 1px solid rgba(232, 62, 130, 0.4);
  color: #FF8BB9;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  padding: 4px 10px;
  border-radius: 999px;
}

.rr-badge-cyan {
  display: inline-flex;
  align-items: center;
  background: rgba(85, 214, 232, 0.12);
  border: 1px solid rgba(85, 214, 232, 0.35);
  color: #72E2EF;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  padding: 4px 10px;
  border-radius: 999px;
}

/* Metric KPI Cards */
.rr-kpi-card {
  background: linear-gradient(145deg, rgba(19, 30, 51, 0.9) 0%, rgba(12, 18, 32, 0.95) 100%);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  padding: 18px 20px;
  position: relative;
  transition: all 0.25s ease;
  box-shadow: 0 4px 16px rgba(0,0,0,0.25);
  min-height: 112px;
}

.rr-kpi-card:hover {
  border-color: rgba(232, 62, 130, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(232, 62, 130, 0.15);
}

.rr-kpi-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-weight: 700;
  color: var(--text-secondary);
}

.rr-kpi-value {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 28px;
  font-weight: 700;
  color: #FFFFFF;
  margin-top: 6px;
}

.rr-kpi-subtext {
  font-size: 11.5px;
  color: var(--text-muted);
  margin-top: 4px;
}

/* Glass Panels */
.rr-panel {
  background: rgba(14, 22, 38, 0.85);
  border: 1px solid var(--border-subtle);
  border-radius: 18px;
  padding: 22px 24px;
  margin-bottom: 20px;
}

.rr-panel-header {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 18px;
  font-weight: 700;
  color: #FFFFFF;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Styled Tabs */
div[data-testid="stTabs"] button {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 600;
  color: #94A3B8;
  border-radius: 8px 8px 0 0;
  padding: 8px 18px;
  transition: all 0.2s ease;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
  color: #FFFFFF !important;
  border-bottom: 2px solid var(--rr-pink) !important;
  background: rgba(232, 62, 130, 0.08);
}

/* Tables and DataFrames */
div[data-testid="stDataFrame"] {
  border: 1px solid var(--border-subtle);
  border-radius: 14px;
  overflow: hidden;
}

/* Custom Buttons */
.stButton > button {
  background: linear-gradient(90deg, #E83E82 0%, #D82F72 100%) !important;
  color: #FFFFFF !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-weight: 700 !important;
  font-size: 13px !important;
  border: none !important;
  border-radius: 10px !important;
  padding: 8px 20px !important;
  transition: all 0.2s ease !important;
}

.stButton > button:hover {
  box-shadow: 0 4px 18px var(--rr-pink-glow) !important;
  transform: translateY(-1px);
}

/* Sliders and Inputs */
div[data-baseweb="slider"] {
  margin-top: 10px;
}

hr {
  border: none;
  height: 1px;
  background: var(--border-subtle);
  margin: 24px 0;
}
</style>
""", unsafe_allow_html=True)

def render_hero_banner(title: str, subtitle: str, badge1: str = "RAJASTHAN ROYALS INTEL", badge2: str = "SEASON 2"):
    """Renders high-impact header banner."""
    st.markdown(f"""
<div class="rr-hero-banner">
  <div style="display:flex; gap:10px; align-items:center;">
    <span class="rr-badge-pink">{badge1}</span>
    <span class="rr-badge-cyan">{badge2}</span>
  </div>
  <div class="rr-hero-title">{title}</div>
  <div class="rr-hero-subtitle">{subtitle}</div>
</div>
""", unsafe_allow_html=True)

def render_kpi(label: str, value: str, subtext: str = ""):
    """Renders a responsive metric card."""
    st.markdown(f"""
<div class="rr-kpi-card">
  <div class="rr-kpi-label">{label}</div>
  <div class="rr-kpi-value">{value}</div>
  <div class="rr-kpi-subtext">{subtext}</div>
</div>
""", unsafe_allow_html=True)
