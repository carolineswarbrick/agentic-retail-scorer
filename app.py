"""
Agentic Retail Readiness Scorer — Streamlit App
Run: streamlit run app.py
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from retailer_db import RETAILERS, SUBVERTICALS
from scorer import score_url, ScoredSite

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Agentic Retail Readiness",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/f/f9/Salesforce.com_logo.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Salesforce design system
# Colours: Navy #032D60, Blue #0176D3, Light Blue #1B96FF, Sky #E8F4FD
# Accent:  Teal #06A59A, Cloud White #FFFFFF, Mid #F3F3F3
# Font stack: Salesforce Sans (via Google Fonts Nunito as proxy), fallback Arial
# ─────────────────────────────────────────────────────────────────────────────

SF_CSS = """
<style>
/* ── Google Font proxy for Salesforce Sans ─────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&display=swap');

/* ── Global resets ─────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Nunito', 'Salesforce Sans', Arial, sans-serif !important;
}

/* ── App background ────────────────────────────────────────────────────── */
.stApp {
    background-color: #032D60;
}

/* ── Sidebar ───────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #032D60 0%, #061F3E 100%) !important;
    border-right: 1px solid #0A4589;
}
[data-testid="stSidebar"] * {
    color: #C9E5FF !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: #C9E5FF !important;
    font-size: 0.95rem;
    padding: 6px 0;
}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"],
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
    color: #FFFFFF !important;
    font-weight: 700;
}

/* ── Main content area ─────────────────────────────────────────────────── */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1280px;
}

/* ── Salesforce top banner ─────────────────────────────────────────────── */
.sf-topbar {
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(90deg, #032D60 0%, #0176D3 60%, #1B96FF 100%);
    border-radius: 12px;
    padding: 18px 28px;
    margin-bottom: 24px;
    box-shadow: 0 4px 24px rgba(1,118,211,0.35);
}
.sf-topbar .sf-logo-text {
    font-size: 1.5rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.02em;
}
.sf-topbar .sf-logo-cloud {
    font-size: 2rem;
    line-height: 1;
}
.sf-topbar .sf-tagline {
    font-size: 0.82rem;
    color: #C9E5FF;
    margin-left: auto;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-weight: 600;
}

/* ── Page headings ─────────────────────────────────────────────────────── */
h1, h2, h3, h4 {
    font-family: 'Nunito', Arial, sans-serif !important;
    color: #FFFFFF !important;
    letter-spacing: -0.01em;
}
h1 { font-size: 2rem !important; font-weight: 800 !important; }
h2 { font-size: 1.35rem !important; font-weight: 700 !important; }
h3 { font-size: 1.1rem !important; font-weight: 700 !important; }

/* ── Metric tiles ──────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #0A3A6E 0%, #0A2E5C 100%);
    border: 1px solid #1B5FA8;
    border-radius: 12px;
    padding: 16px 20px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.25);
}
[data-testid="stMetricLabel"] {
    color: #7AB8F5 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 700 !important;
}
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 1.6rem !important;
    font-weight: 800 !important;
}

/* ── Grade display ─────────────────────────────────────────────────────── */
.sf-grade {
    display: inline-block;
    font-size: 3rem;
    font-weight: 800;
    line-height: 1;
    text-align: center;
    width: 100%;
    padding: 8px 0 4px;
    letter-spacing: -0.02em;
}
.grade-A { color: #04E0A8; }
.grade-B { color: #4BCA81; }
.grade-C { color: #FFB75D; }
.grade-D { color: #FE9339; }
.grade-F { color: #FE5C4C; }

/* ── Score bar ─────────────────────────────────────────────────────────── */
.sf-bar-wrap {
    background: #0A2E5C;
    border-radius: 100px;
    height: 8px;
    overflow: hidden;
    margin: 6px 0 4px;
}
.sf-bar-fill {
    height: 100%;
    border-radius: 100px;
    transition: width 0.4s ease;
}
.sf-bar-label {
    font-size: 0.78rem;
    color: #7AB8F5;
    font-weight: 600;
}

/* ── Buttons ───────────────────────────────────────────────────────────── */
.stButton > button {
    font-family: 'Nunito', Arial, sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.01em;
    border-radius: 100px !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0176D3, #1B96FF) !important;
    border: none !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 8px rgba(1,118,211,0.4) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #015BA7, #0176D3) !important;
    box-shadow: 0 4px 16px rgba(1,118,211,0.55) !important;
    transform: translateY(-1px);
}
.stButton > button:not([kind="primary"]) {
    background: transparent !important;
    border: 1.5px solid #1B96FF !important;
    color: #1B96FF !important;
}
.stButton > button:not([kind="primary"]):hover {
    background: rgba(27,150,255,0.1) !important;
}

/* ── Text input ────────────────────────────────────────────────────────── */
.stTextInput > div > div > input {
    background: #0A2E5C !important;
    border: 1.5px solid #1B5FA8 !important;
    border-radius: 100px !important;
    color: #FFFFFF !important;
    padding: 10px 20px !important;
    font-family: 'Nunito', Arial, sans-serif !important;
    font-size: 0.95rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #1B96FF !important;
    box-shadow: 0 0 0 3px rgba(27,150,255,0.2) !important;
}
.stTextInput > div > div > input::placeholder {
    color: #4D86BA !important;
}

/* ── Expanders (check results) ─────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: linear-gradient(135deg, #0A3A6E 0%, #062448 100%) !important;
    border: 1px solid #1B5FA8 !important;
    border-radius: 12px !important;
    margin-bottom: 10px !important;
    overflow: hidden;
}
[data-testid="stExpander"] summary {
    color: #C9E5FF !important;
    font-weight: 700 !important;
    font-size: 0.9rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    padding: 14px 18px !important;
}
[data-testid="stExpander"] summary:hover {
    background: rgba(27,150,255,0.08) !important;
}

/* ── Divider ───────────────────────────────────────────────────────────── */
hr {
    border-color: #1B5FA8 !important;
    opacity: 0.4;
    margin: 20px 0 !important;
}

/* ── Dataframe ─────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #1B5FA8 !important;
    border-radius: 12px !important;
    overflow: hidden;
}

/* ── Multiselect / select ──────────────────────────────────────────────── */
.stMultiSelect [data-baseweb="select"] > div,
.stSelectbox [data-baseweb="select"] > div {
    background: #0A2E5C !important;
    border-color: #1B5FA8 !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
}

/* ── Slider ────────────────────────────────────────────────────────────── */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: #1B96FF !important;
}

/* ── Progress bar ──────────────────────────────────────────────────────── */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #0176D3, #1B96FF) !important;
    border-radius: 100px !important;
}

/* ── Info / warning / success boxes ───────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: none !important;
    font-family: 'Nunito', Arial, sans-serif !important;
}

/* ── Caption / small text ──────────────────────────────────────────────── */
.stCaption, [data-testid="stCaptionContainer"] {
    color: #7AB8F5 !important;
}

/* ── Checkbox ──────────────────────────────────────────────────────────── */
[data-testid="stCheckbox"] label {
    color: #C9E5FF !important;
}

/* ── SF pill badge ─────────────────────────────────────────────────────── */
.sf-pill {
    display: inline-block;
    background: rgba(27,150,255,0.18);
    border: 1px solid #1B96FF;
    border-radius: 100px;
    padding: 2px 12px;
    font-size: 0.78rem;
    font-weight: 700;
    color: #7AB8F5;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* ── SF card ───────────────────────────────────────────────────────────── */
.sf-card {
    background: linear-gradient(135deg, #0A3A6E 0%, #062448 100%);
    border: 1px solid #1B5FA8;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

/* ── Check row ─────────────────────────────────────────────────────────── */
.check-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid rgba(27,95,168,0.25);
}
.check-row:last-child { border-bottom: none; }
.check-icon { font-size: 1rem; flex-shrink: 0; padding-top: 2px; }
.check-name { font-weight: 700; color: #FFFFFF; font-size: 0.9rem; min-width: 200px; }
.check-score {
    font-family: monospace;
    font-size: 0.82rem;
    background: rgba(27,150,255,0.15);
    border: 1px solid #1B5FA8;
    border-radius: 6px;
    padding: 1px 8px;
    color: #7AB8F5;
    white-space: nowrap;
}
.check-detail { font-size: 0.82rem; color: #7AB8F5; flex: 1; }

/* ── Sidebar nav active item ───────────────────────────────────────────── */
.sf-nav-item {
    padding: 10px 14px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    font-size: 0.9rem;
    color: #C9E5FF;
    margin-bottom: 4px;
    transition: background 0.15s;
}
.sf-nav-item.active {
    background: rgba(27,150,255,0.2);
    color: #FFFFFF;
    border-left: 3px solid #1B96FF;
}

/* ── Download button ───────────────────────────────────────────────────── */
.stDownloadButton > button {
    border-radius: 100px !important;
    font-weight: 700 !important;
    background: transparent !important;
    border: 1.5px solid #04E0A8 !important;
    color: #04E0A8 !important;
}
.stDownloadButton > button:hover {
    background: rgba(4,224,168,0.1) !important;
}

/* ── Plotly chart background transparency ──────────────────────────────── */
.js-plotly-plot .plotly .bg {
    fill: transparent !important;
}
</style>
"""

st.markdown(SF_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Salesforce top banner
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="sf-topbar">
  <img src="https://upload.wikimedia.org/wikipedia/commons/f/f9/Salesforce.com_logo.svg"
       alt="Salesforce" style="height:36px;width:auto;flex-shrink:0;" />
  <span class="sf-logo-text" style="font-weight:400;color:#C9E5FF;font-size:1.3rem;">Agentic Retail Intelligence</span>
  <span class="sf-tagline">Powered by Agentforce &nbsp;·&nbsp; Australia</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Password gate
# ─────────────────────────────────────────────────────────────────────────────

def _check_password() -> bool:
    if st.session_state.get("_authenticated"):
        return True
    correct = st.secrets.get("APP_PASSWORD", "")
    st.markdown("""
    <div style="max-width:400px;margin:80px auto 0;">
      <div style="text-align:center;margin-bottom:32px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/f/f9/Salesforce.com_logo.svg"
             style="height:48px;width:auto;" alt="Salesforce" />
        <p style="color:#7AB8F5;font-size:0.9rem;margin-top:12px;">Agentic Retail Intelligence</p>
      </div>
    </div>
    """, unsafe_allow_html=True)
    col = st.columns([1, 2, 1])[1]
    with col:
        pwd = st.text_input("Password", type="password", placeholder="Enter access password",
                            label_visibility="collapsed")
        if st.button("Access →", type="primary", use_container_width=True):
            if pwd == correct:
                st.session_state["_authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    return False

if not _check_password():
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────

if "baseline_results" not in st.session_state:
    st.session_state.baseline_results = {}
if "single_results" not in st.session_state:
    st.session_state.single_results = {}
# Overrides set by the user on the baseline / category tabs
if "sv_filter_override" not in st.session_state:
    st.session_state.sv_filter_override = []
if "tier_filter_override" not in st.session_state:
    st.session_state.tier_filter_override = []

# ─────────────────────────────────────────────────────────────────────────────
# Design tokens & helpers
# ─────────────────────────────────────────────────────────────────────────────

SF_BLUE       = "#0176D3"
SF_LIGHT_BLUE = "#1B96FF"
SF_TEAL       = "#04E0A8"
SF_NAVY       = "#032D60"
SF_MID_NAVY   = "#0A3A6E"
SF_AMBER      = "#FFB75D"
SF_ORANGE     = "#FE9339"
SF_RED        = "#FE5C4C"
SF_GREEN      = "#4BCA81"

GRADE_COLORS = {
    "A": SF_TEAL,
    "B": SF_GREEN,
    "C": SF_AMBER,
    "D": SF_ORANGE,
    "F": SF_RED,
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(10,42,92,0.4)",
    font=dict(family="Nunito, Arial, sans-serif", color="#C9E5FF"),
    title_font=dict(color="#FFFFFF", size=15, family="Nunito, Arial, sans-serif"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#C9E5FF")),
    xaxis=dict(gridcolor="rgba(27,95,168,0.3)", tickfont=dict(color="#7AB8F5"), title_font=dict(color="#7AB8F5")),
    yaxis=dict(gridcolor="rgba(27,95,168,0.3)", tickfont=dict(color="#7AB8F5"), title_font=dict(color="#7AB8F5")),
)


def score_bar_html(score: float, color: str = SF_BLUE) -> str:
    pct = max(0, min(100, score))
    return (
        f'<div class="sf-bar-wrap"><div class="sf-bar-fill" style="width:{pct}%;background:{color};"></div></div>'
        f'<span class="sf-bar-label">{pct:.0f} / 100</span>'
    )


def grade_html(grade: str) -> str:
    color = GRADE_COLORS.get(grade, "#7AB8F5")
    return f'<div class="sf-grade grade-{grade}" style="color:{color};">{grade}</div>'


def detect_subvertical(domain: str) -> str:
    """Return the subvertical for a known domain, else 'Unknown'."""
    for r in RETAILERS:
        if r["domain"] == domain or domain.endswith("." + r["domain"]) or r["domain"].endswith("." + domain):
            return r["subvertical"]
    # fuzzy: strip www and match root
    root = domain.replace("www.", "").split("/")[0]
    for r in RETAILERS:
        r_root = r["domain"].replace("www.", "").split("/")[0]
        if root == r_root or root.endswith("." + r_root) or r_root.endswith("." + root):
            return r["subvertical"]
    return "Unknown"


def category_peers(subvertical: str, scored_domain: str) -> list:
    """All retailers in the same subvertical, including ones not yet scanned."""
    return [r for r in RETAILERS if r["subvertical"] == subvertical and r["domain"] != scored_domain]


def results_to_df(results: dict, retailer_meta: dict = None) -> pd.DataFrame:
    rows = []
    for url, r in results.items():
        meta = (retailer_meta or {}).get(r.domain, {})
        rows.append({
            "Domain": r.domain,
            "Name": meta.get("name", r.domain),
            "Subvertical": meta.get("subvertical", "Unknown"),
            "Traffic Tier": meta.get("traffic", "—"),
            "Overall": r.overall_score,
            "Trust": r.trust_score,
            "Readiness": r.readiness_score,
            "Grade": r.grade,
            "Error": r.error or "",
        })
    return pd.DataFrame(rows).sort_values("Overall", ascending=False)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar navigation
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;color:#4D86BA;font-weight:700;margin-bottom:12px;">Navigation</p>', unsafe_allow_html=True)
    page = st.radio(
        "nav",
        ["Score a URL", "Australian Baseline", "Category Analysis", "Methodology"],
        label_visibility="collapsed",
    )
    st.markdown('<hr style="border-color:#1B5FA8;opacity:0.4;margin:20px 0;">', unsafe_allow_html=True)
    st.markdown("""
    <p style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;color:#4D86BA;font-weight:700;margin-bottom:10px;">Signals Checked</p>
    <p style="font-size:0.78rem;color:#7AB8F5;line-height:1.7;">
    HTTPS &nbsp;·&nbsp; Security Headers<br>
    Privacy &amp; Returns Policy<br>
    Dark Patterns<br>
    AI Bot Directives &nbsp;·&nbsp; llms.txt<br>
    Schema.org Markup<br>
    Product Data Richness<br>
    Sitemap &nbsp;·&nbsp; Search<br>
    Guest Checkout &nbsp;·&nbsp; BNPL<br>
    Headless / API Signals<br>
    Accessibility &nbsp;·&nbsp; Performance
    </p>
    """, unsafe_allow_html=True)
    st.markdown('<hr style="border-color:#1B5FA8;opacity:0.4;margin:20px 0;">', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;">
      <img src="https://upload.wikimedia.org/wikipedia/commons/f/f9/Salesforce.com_logo.svg"
           alt="Salesforce" style="height:22px;width:auto;opacity:0.6;" />
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Score a URL
# ─────────────────────────────────────────────────────────────────────────────

if page == "Score a URL":
    st.markdown("## Score Any Retailer")
    st.markdown('<p style="color:#7AB8F5;margin-top:-12px;margin-bottom:20px;">Enter any retailer URL to run a full Agentic Readiness assessment powered by Agentforce intelligence.</p>', unsafe_allow_html=True)

    col_in, col_btn = st.columns([4, 1])
    with col_in:
        input_url = st.text_input(
            "url",
            placeholder="e.g.  woolworths.com.au  or  https://www.kogan.com",
            label_visibility="collapsed",
        )
    with col_btn:
        run_btn = st.button("Analyse ▶", type="primary", use_container_width=True)

    if run_btn and input_url.strip():
        with st.spinner("Analysing retailer..."):
            result = score_url(input_url.strip())
        st.session_state.single_results[input_url.strip()] = result
        # Flag that peers need scanning — the scan runs below after results render
        _sv_for_scan = detect_subvertical(result.domain)
        _peers_to_scan = (
            [p for p in category_peers(_sv_for_scan, result.domain)
             if p["domain"] not in st.session_state.baseline_results]
            if _sv_for_scan != "Unknown" else []
        )
        st.session_state["_pending_peer_scan"] = _peers_to_scan
        st.session_state["_pending_peer_sv"]   = _sv_for_scan

    # ── Active filter banner + revert ─────────────────────────────────────
    has_overrides = bool(st.session_state.sv_filter_override or st.session_state.tier_filter_override)
    if has_overrides:
        ov_parts = []
        if st.session_state.sv_filter_override:
            ov_parts.append("Subvertical: " + ", ".join(st.session_state.sv_filter_override))
        if st.session_state.tier_filter_override:
            ov_parts.append("Traffic Tier: " + ", ".join(st.session_state.tier_filter_override))
        banner_col, revert_col = st.columns([5, 1])
        with banner_col:
            st.info(f"ℹ  Active filters from Baseline/Category tabs — {' · '.join(ov_parts)}")
        with revert_col:
            if st.button("↩  Revert to default", use_container_width=True):
                st.session_state.sv_filter_override = []
                st.session_state.tier_filter_override = []
                st.rerun()

    if st.session_state.single_results:
        latest_url = list(st.session_state.single_results.keys())[-1]
        r = st.session_state.single_results[latest_url]

        if r.error:
            st.warning(f"⚠  {r.error} — partial results shown.")

        st.markdown("---")

        # ── Detect subvertical & gather peers ─────────────────────────────
        meta_lookup = {ret["domain"]: ret for ret in RETAILERS}
        subvertical = detect_subvertical(r.domain)
        peers = category_peers(subvertical, r.domain)

        # Apply any active overrides to which peers show
        if st.session_state.sv_filter_override:
            peers = [p for p in peers if p["subvertical"] in st.session_state.sv_filter_override]
        if st.session_state.tier_filter_override:
            peers = [p for p in peers if p["traffic"] in st.session_state.tier_filter_override]

        # Collect already-scanned peer scores from baseline results
        peer_scores = {}
        for p in peers:
            if p["domain"] in st.session_state.baseline_results:
                peer_scores[p["domain"]] = st.session_state.baseline_results[p["domain"]]

        # ── Compute category averages from all scanned peers ───────────────
        all_category_scored = list(peer_scores.values())
        if all_category_scored:
            cat_avg_trust     = sum(s.trust_score     for s in all_category_scored) / len(all_category_scored)
            cat_avg_readiness = sum(s.readiness_score for s in all_category_scored) / len(all_category_scored)
            cat_avg_overall   = sum(s.overall_score   for s in all_category_scored) / len(all_category_scored)
        else:
            cat_avg_trust = cat_avg_readiness = cat_avg_overall = None

        def _avg_bar_html(retailer_score, avg_score, color, avg_color="#FFB75D"):
            pct = max(0, min(100, retailer_score))
            avg_pct = max(0, min(100, avg_score)) if avg_score is not None else None
            bar = (
                f'<div style="position:relative;background:#0A2E5C;border-radius:100px;height:8px;overflow:visible;margin:6px 0 2px;">'
                f'<div style="width:{pct}%;height:100%;background:{color};border-radius:100px;"></div>'
            )
            if avg_pct is not None:
                bar += (
                    f'<div style="position:absolute;top:-3px;left:{avg_pct}%;width:2px;height:14px;'
                    f'background:{avg_color};border-radius:2px;" title="Category avg: {avg_score:.0f}"></div>'
                )
            bar += '</div>'
            score_line = f'<span style="color:#FFFFFF;font-size:0.82rem;font-weight:700;">{retailer_score:.0f}/100</span>'
            if avg_pct is not None:
                delta = retailer_score - avg_score
                delta_color = SF_TEAL if delta >= 0 else SF_RED
                delta_sign = "+" if delta >= 0 else ""
                score_line += (
                    f'&ensp;<span style="color:#FFB75D;font-size:0.75rem;">cat. avg {avg_score:.0f}</span>'
                    f'&ensp;<span style="color:{delta_color};font-size:0.75rem;font-weight:700;">{delta_sign}{delta:.0f}</span>'
                )
            return bar + score_line

        # ── Score cards ────────────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Overall Score", f"{r.overall_score}")
            st.markdown(grade_html(r.grade), unsafe_allow_html=True)
            if cat_avg_overall is not None:
                st.markdown(
                    f'<p style="color:#7AB8F5;font-size:0.72rem;margin-top:6px;">Category avg: '
                    f'<span style="color:#FFB75D;font-weight:700;">{cat_avg_overall:.0f}/100</span></p>',
                    unsafe_allow_html=True,
                )
        with c2:
            st.metric("Agentic Trust", f"{r.trust_score}")
            st.markdown(_avg_bar_html(r.trust_score, cat_avg_trust, SF_BLUE), unsafe_allow_html=True)
        with c3:
            st.metric("Agentic Readiness", f"{r.readiness_score}")
            st.markdown(_avg_bar_html(r.readiness_score, cat_avg_readiness, SF_TEAL), unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0A3A6E 0%,#0A2E5C 100%);border:1px solid #1B5FA8;border-radius:12px;padding:16px 20px;box-shadow:0 2px 12px rgba(0,0,0,0.25);">
              <p style="color:#7AB8F5;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.06em;font-weight:700;margin:0 0 6px 0;">Domain</p>
              <p style="color:#FFFFFF;font-size:1rem;font-weight:800;margin:0 0 6px 0;word-break:break-all;line-height:1.3;">{r.domain}</p>
              <p style="color:#7AB8F5;font-size:0.78rem;margin:0 0 4px 0;">Analysed {datetime.now().strftime("%d %b %Y, %H:%M")}</p>
              {"" if subvertical == "Unknown" else f'<span class="sf-pill">{subvertical}</span>'}
              {"" if cat_avg_overall is None else f'<p style="color:#7AB8F5;font-size:0.72rem;margin-top:6px;">{len(all_category_scored)} peers scanned</p>'}
            </div>
            """, unsafe_allow_html=True)

        # ── Category peer comparison bar ───────────────────────────────────
        st.markdown("---")
        if subvertical != "Unknown":
            sv_label = f'<span class="sf-pill">{subvertical}</span>'
            scanned_count = len(peer_scores)
            total_peers = len(peers)
            avg_str = (
                f'&nbsp;·&nbsp; <span style="color:#FFB75D;font-weight:700;">cat. avg {cat_avg_overall:.0f}/100</span>'
                if cat_avg_overall is not None else ""
            )
            st.markdown(
                f'<p style="color:#C9E5FF;font-size:0.9rem;margin-bottom:12px;">'
                f'Category {sv_label} &nbsp;·&nbsp; '
                f'<span style="color:#7AB8F5;">{scanned_count}/{total_peers} peers scanned</span>'
                f'{avg_str}</p>',
                unsafe_allow_html=True,
            )

            # Build comparison rows: scored site first, then all peers (scanned ones show score, unscanned show "—")
            rows_html = ""

            def _peer_bar(score, color, width_basis=100):
                pct = max(0, min(width_basis, score))
                return (
                    f'<div style="flex:1;background:#0A2E5C;border-radius:100px;height:8px;overflow:hidden;margin:0 10px;">'
                    f'<div style="width:{pct}%;height:100%;background:{color};border-radius:100px;"></div></div>'
                )

            def _row(name, domain, overall, trust, readiness, is_subject=False):
                border = f"border:1.5px solid {SF_LIGHT_BLUE};" if is_subject else "border:1px solid #1B5FA8;"
                bg = "background:rgba(27,150,255,0.1);" if is_subject else "background:rgba(10,46,92,0.5);"
                tag = f'<span style="font-size:0.7rem;background:{SF_LIGHT_BLUE};color:#032D60;border-radius:4px;padding:1px 7px;font-weight:800;margin-left:6px;">YOU</span>' if is_subject else ""
                if overall is None:
                    score_cell = '<span style="color:#4D86BA;font-size:0.82rem;">not yet scanned</span>'
                    bar_trust = _peer_bar(0, SF_BLUE)
                    bar_ready = _peer_bar(0, SF_TEAL)
                    overall_str = "—"
                else:
                    score_cell = f'<span style="color:#FFFFFF;font-weight:800;font-size:0.95rem;">{overall}</span>'
                    bar_trust = _peer_bar(trust, SF_BLUE)
                    bar_ready = _peer_bar(readiness, SF_TEAL)
                    overall_str = str(overall)
                return f"""
                <div style="display:flex;align-items:center;gap:8px;padding:9px 14px;border-radius:10px;margin-bottom:6px;{border}{bg}">
                  <div style="min-width:180px;max-width:180px;">
                    <span style="color:#FFFFFF;font-size:0.85rem;font-weight:700;word-break:break-all;">{name}{tag}</span>
                    <div style="color:#4D86BA;font-size:0.72rem;word-break:break-all;">{domain}</div>
                  </div>
                  <div style="display:flex;align-items:center;flex:1;gap:4px;">
                    <span style="color:#7AB8F5;font-size:0.7rem;min-width:32px;">Trust</span>
                    {bar_trust}
                    <span style="color:#7AB8F5;font-size:0.7rem;min-width:28px;text-align:right;">{trust if overall is not None else "—"}</span>
                  </div>
                  <div style="display:flex;align-items:center;flex:1;gap:4px;">
                    <span style="color:#04E0A8;font-size:0.7rem;min-width:48px;">Readiness</span>
                    {bar_ready}
                    <span style="color:#04E0A8;font-size:0.7rem;min-width:28px;text-align:right;">{readiness if overall is not None else "—"}</span>
                  </div>
                  <div style="min-width:48px;text-align:right;">{score_cell}</div>
                </div>"""

            # Subject row first
            subj_meta = meta_lookup.get(r.domain, {})
            subj_name = subj_meta.get("name", r.domain)
            rows_html += _row(subj_name, r.domain, r.overall_score, r.trust_score, r.readiness_score, is_subject=True)

            # Peer rows — scanned first (sorted by overall desc), then unscanned alphabetically
            scanned_peers = sorted(
                [(p, peer_scores[p["domain"]]) for p in peers if p["domain"] in peer_scores],
                key=lambda x: x[1].overall_score, reverse=True,
            )
            unscanned_peers = [p for p in peers if p["domain"] not in peer_scores]

            for p, ps in scanned_peers:
                rows_html += _row(p["name"], p["domain"], ps.overall_score, ps.trust_score, ps.readiness_score)
            for p in unscanned_peers:
                rows_html += _row(p["name"], p["domain"], None, None, None)

            st.markdown(rows_html, unsafe_allow_html=True)

            if unscanned_peers:
                st.caption(f"{len(unscanned_peers)} peers shown as 'not yet scanned' were not reachable during the auto-scan.")
        else:
            st.markdown('<p style="color:#4D86BA;font-size:0.85rem;">Domain not found in the Australian retailer database — no category peers available.</p>', unsafe_allow_html=True)

        st.markdown("---")

        # ── Radar chart ────────────────────────────────────────────────────
        cats = r.checks_by_category()
        cat_scores = {}
        for cat, chks in cats.items():
            tw = sum(c.weight for c in chks)
            cat_scores[cat] = (sum(c.score * c.weight for c in chks) / tw * 100) if tw else 0

        labels_raw = list(cat_scores.keys())
        values = list(cat_scores.values())
        labels = [l.split(": ")[-1] for l in labels_raw]

        fig_radar = go.Figure(go.Scatterpolar(
            r=values + [values[0]],
            theta=labels + [labels[0]],
            fill="toself",
            fillcolor="rgba(1,118,211,0.18)",
            line=dict(color=SF_LIGHT_BLUE, width=2),
            name=r.domain,
            marker=dict(color=SF_LIGHT_BLUE, size=6),
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True, range=[0, 100],
                    gridcolor="rgba(27,95,168,0.4)",
                    tickfont=dict(color="#7AB8F5", size=10),
                    tickcolor="#7AB8F5",
                ),
                angularaxis=dict(tickfont=dict(color="#C9E5FF", size=11)),
                bgcolor="rgba(10,46,92,0.5)",
            ),
            showlegend=False,
            height=360,
            margin=dict(l=50, r=50, t=30, b=30),
            **{k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("xaxis", "yaxis")},
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # ── Detailed checks ────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### Detailed Check Results")

        for cat, chks in cats.items():
            label = cat.split(": ")[-1]
            cat_score = cat_scores.get(cat, 0)
            with st.expander(f"{cat}  —  {cat_score:.0f}/100", expanded=True):
                rows_html = ""
                for c in chks:
                    icon = "✅" if c.passed else "❌"
                    sc_pct = f"{c.score * 100:.0f}%"
                    rows_html += f"""
                    <div class="check-row">
                      <span class="check-icon">{icon}</span>
                      <span class="check-name">{c.name}</span>
                      <span class="check-score">{sc_pct}</span>
                      <span class="check-detail">{c.detail}</span>
                    </div>"""
                st.markdown(rows_html, unsafe_allow_html=True)

        # ── Session comparison ─────────────────────────────────────────────
        if len(st.session_state.single_results) > 1:
            st.markdown("---")
            st.markdown("### Session Comparison")
            compare_df = pd.DataFrame([
                {
                    "Domain": s.domain,
                    "Trust": s.trust_score,
                    "Readiness": s.readiness_score,
                    "Overall": s.overall_score,
                    "Grade": s.grade,
                }
                for s in st.session_state.single_results.values()
            ])
            fig_cmp = px.bar(
                compare_df, x="Domain", y=["Trust", "Readiness"],
                barmode="group",
                title="Trust vs Readiness — Session Comparison",
                labels={"value": "Score", "variable": "Dimension"},
                color_discrete_map={"Trust": SF_BLUE, "Readiness": SF_TEAL},
            )
            fig_cmp.update_traces(marker_line_width=0)
            fig_cmp.update_layout(height=380, **PLOTLY_LAYOUT)
            st.plotly_chart(fig_cmp, use_container_width=True)

    # ── Category peer auto-scan (runs after results are on screen) ─────────
    _pending = st.session_state.get("_pending_peer_scan", [])
    _pending_sv = st.session_state.get("_pending_peer_sv", "")
    if _pending:
        st.session_state["_pending_peer_scan"] = []  # clear immediately to avoid re-run loops
        _prog = st.progress(0, text=f"Scanning {len(_pending)} {_pending_sv} category peers...")
        _completed = 0

        def _scan_peer(retailer):
            return retailer["domain"], score_url("https://" + retailer["domain"])

        with ThreadPoolExecutor(max_workers=6) as _ex:
            _futures = {_ex.submit(_scan_peer, p): p for p in _pending}
            for _fut in as_completed(_futures):
                _dom, _res = _fut.result()
                st.session_state.baseline_results[_dom] = _res
                _completed += 1
                _prog.progress(_completed / len(_pending),
                               text=f"Category scan {_completed}/{len(_pending)} — {_dom}")
        _prog.empty()
        st.rerun()  # refresh page so averages and peer bars update with new data


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Australian Baseline
# ─────────────────────────────────────────────────────────────────────────────

elif page == "Australian Baseline":
    st.markdown("## Australian Retail Baseline")
    st.markdown(f'<p style="color:#7AB8F5;margin-top:-12px;margin-bottom:20px;">Pre-curated database of <strong style="color:#FFFFFF;">{len(RETAILERS)}</strong> top Australian retailers. Scan to build a full agentic readiness benchmark.</p>', unsafe_allow_html=True)

    meta_lookup = {r["domain"]: r for r in RETAILERS}

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        sv_filter = st.multiselect("Subvertical", options=SUBVERTICALS,
                                   default=st.session_state.sv_filter_override)
    with col_f2:
        tier_filter = st.multiselect("Traffic Tier", options=["High", "Medium", "Low"],
                                     default=st.session_state.tier_filter_override)
    with col_f3:
        scanned_only = st.checkbox("Show scanned only", value=False)

    # Persist so Score a URL tab reflects changes
    st.session_state.sv_filter_override = sv_filter
    st.session_state.tier_filter_override = tier_filter

    filtered = RETAILERS.copy()
    if sv_filter:
        filtered = [r for r in filtered if r["subvertical"] in sv_filter]
    if tier_filter:
        filtered = [r for r in filtered if r["traffic"] in tier_filter]

    st.markdown("---")
    n_to_scan = st.slider(
        "Sites to scan",
        1, len(filtered), min(20, len(filtered)),
        help="Each site takes ~8–15 seconds. Scans run 5 in parallel.",
    )
    targets = filtered[:n_to_scan]

    col_scan, col_clear = st.columns([2, 1])
    with col_scan:
        scan_btn = st.button(f"▶  Scan {len(targets)} sites", type="primary", use_container_width=True)
    with col_clear:
        if st.button("Clear results", use_container_width=True):
            st.session_state.baseline_results = {}
            st.rerun()

    if scan_btn:
        progress = st.progress(0, text="Initialising scan...")
        total = len(targets)

        def _scan_one(retailer):
            url = "https://" + retailer["domain"]
            return retailer["domain"], score_url(url)

        completed = 0
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(_scan_one, r): r for r in targets}
            for future in as_completed(futures):
                domain, result = future.result()
                st.session_state.baseline_results[domain] = result
                completed += 1
                progress.progress(completed / total, text=f"Scanning {completed}/{total} — {domain}")
        progress.empty()
        st.success(f"Scan complete — {completed} sites analysed.")

    all_results = st.session_state.baseline_results
    if all_results:
        df = results_to_df(all_results, meta_lookup)
        if sv_filter:
            df = df[df["Subvertical"].isin(sv_filter)]
        if tier_filter:
            df = df[df["Traffic Tier"].isin(tier_filter)]

        st.markdown("---")
        st.markdown(f"### Results — {len(df)} sites scanned")

        # KPI row
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Avg Overall", f"{df['Overall'].mean():.1f}")
        mc2.metric("Avg Agentic Trust", f"{df['Trust'].mean():.1f}")
        mc3.metric("Avg Agentic Readiness", f"{df['Readiness'].mean():.1f}")
        grade_counts = df["Grade"].value_counts()
        mc4.metric("Grade A Sites", int(grade_counts.get("A", 0)))

        # Scatter
        st.markdown("---")
        fig_scatter = px.scatter(
            df, x="Trust", y="Readiness", text="Name",
            color="Subvertical",
            size=[10] * len(df), size_max=14,
            title="Agentic Trust vs Readiness Matrix",
            labels={"Trust": "Agentic Trust Score", "Readiness": "Agentic Readiness Score"},
            hover_data=["Traffic Tier", "Overall", "Grade"],
        )
        fig_scatter.update_traces(textposition="top center", textfont=dict(size=9, color="#C9E5FF"))
        fig_scatter.add_hline(y=50, line_dash="dot", line_color="#1B5FA8",
                              annotation_text="Readiness midpoint", annotation_font_color="#7AB8F5")
        fig_scatter.add_vline(x=50, line_dash="dot", line_color="#1B5FA8",
                              annotation_text="Trust midpoint", annotation_font_color="#7AB8F5")
        fig_scatter.update_layout(height=520, **PLOTLY_LAYOUT)
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Table
        st.dataframe(
            df[["Name", "Subvertical", "Traffic Tier", "Overall", "Trust", "Readiness", "Grade"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Overall":    st.column_config.ProgressColumn("Overall",    min_value=0, max_value=100, format="%d"),
                "Trust":      st.column_config.ProgressColumn("Trust",      min_value=0, max_value=100, format="%d"),
                "Readiness":  st.column_config.ProgressColumn("Readiness",  min_value=0, max_value=100, format="%d"),
            },
        )

        st.download_button(
            "⬇  Export CSV",
            df.to_csv(index=False),
            file_name=f"sf_agentic_baseline_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )
    else:
        st.markdown("---")
        preview_df = pd.DataFrame(filtered)[["name", "domain", "subvertical", "traffic"]]
        preview_df.columns = ["Name", "Domain", "Subvertical", "Traffic Tier"]
        st.dataframe(preview_df, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Category Analysis
# ─────────────────────────────────────────────────────────────────────────────

elif page == "Category Analysis":
    st.markdown("## Category & Subvertical Analysis")

    if not st.session_state.baseline_results:
        st.info("Run the **Australian Baseline** scan first to populate data here.")
    else:
        meta_lookup = {r["domain"]: r for r in RETAILERS}
        df = results_to_df(st.session_state.baseline_results, meta_lookup)

        cat_df = df.groupby("Subvertical").agg(
            Sites=("Domain", "count"),
            Avg_Overall=("Overall", "mean"),
            Avg_Trust=("Trust", "mean"),
            Avg_Readiness=("Readiness", "mean"),
        ).reset_index().sort_values("Avg_Overall", ascending=False)

        # Category bar chart
        st.markdown("### Category Leaderboard")
        fig_cat = px.bar(
            cat_df, x="Subvertical", y=["Avg_Trust", "Avg_Readiness"],
            barmode="group",
            labels={"value": "Score", "variable": "Dimension"},
            title="Average Trust & Readiness by Subvertical",
            color_discrete_map={"Avg_Trust": SF_BLUE, "Avg_Readiness": SF_TEAL},
        )
        fig_cat.update_xaxes(tickangle=40)
        fig_cat.update_traces(marker_line_width=0)
        fig_cat.update_layout(height=460, **PLOTLY_LAYOUT)
        st.plotly_chart(fig_cat, use_container_width=True)

        # Category table
        cat_df_display = cat_df.copy()
        for col in ["Avg_Overall", "Avg_Trust", "Avg_Readiness"]:
            cat_df_display[col] = cat_df_display[col].round(1)
        st.dataframe(
            cat_df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Avg_Overall":    st.column_config.ProgressColumn("Avg Overall",    min_value=0, max_value=100, format="%.1f"),
                "Avg_Trust":      st.column_config.ProgressColumn("Avg Trust",      min_value=0, max_value=100, format="%.1f"),
                "Avg_Readiness":  st.column_config.ProgressColumn("Avg Readiness",  min_value=0, max_value=100, format="%.1f"),
            },
        )

        # Heatmap
        st.markdown("---")
        st.markdown("### Score Heatmap")
        heatmap_data = cat_df.set_index("Subvertical")[["Avg_Trust", "Avg_Readiness", "Avg_Overall"]].round(1)
        fig_heat = px.imshow(
            heatmap_data.T,
            text_auto=True,
            color_continuous_scale=[[0, "#FE5C4C"], [0.5, "#FFB75D"], [1, "#04E0A8"]],
            range_color=[0, 100],
            labels={"x": "Subvertical", "y": "Dimension", "color": "Score"},
            title="Score Heatmap — Category × Dimension",
        )
        fig_heat.update_xaxes(tickangle=40)
        fig_heat.update_layout(height=260, **{k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("xaxis", "yaxis")})
        st.plotly_chart(fig_heat, use_container_width=True)

        # Traffic tier
        st.markdown("---")
        st.markdown("### Does Traffic Tier Predict Readiness?")
        tier_df = df.groupby("Traffic Tier").agg(
            Sites=("Domain", "count"),
            Avg_Overall=("Overall", "mean"),
            Avg_Trust=("Trust", "mean"),
            Avg_Readiness=("Readiness", "mean"),
        ).reset_index()
        fig_tier = px.bar(
            tier_df, x="Traffic Tier", y=["Avg_Trust", "Avg_Readiness"],
            barmode="group",
            title="Average Scores by Traffic Tier",
            color_discrete_map={"Avg_Trust": SF_BLUE, "Avg_Readiness": SF_TEAL},
        )
        fig_tier.update_traces(marker_line_width=0)
        fig_tier.update_layout(height=360, **PLOTLY_LAYOUT)
        st.plotly_chart(fig_tier, use_container_width=True)

        # Grade distribution
        st.markdown("---")
        st.markdown("### Grade Distribution by Subvertical")
        grade_df = df.groupby(["Subvertical", "Grade"]).size().reset_index(name="Count")
        fig_grade = px.bar(
            grade_df, x="Subvertical", y="Count", color="Grade",
            title="Grade Distribution",
            color_discrete_map=GRADE_COLORS,
        )
        fig_grade.update_xaxes(tickangle=40)
        fig_grade.update_traces(marker_line_width=0)
        fig_grade.update_layout(height=420, **PLOTLY_LAYOUT)
        st.plotly_chart(fig_grade, use_container_width=True)

        # Drill-down
        st.markdown("---")
        st.markdown("### Subvertical Drill-Down")
        selected_sv = st.selectbox("Select a subvertical", options=sorted(df["Subvertical"].unique()))
        sv_df = df[df["Subvertical"] == selected_sv].sort_values("Overall", ascending=False)
        if not sv_df.empty:
            st.dataframe(
                sv_df[["Name", "Traffic Tier", "Overall", "Trust", "Readiness", "Grade"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Overall":   st.column_config.ProgressColumn("Overall",   min_value=0, max_value=100, format="%d"),
                    "Trust":     st.column_config.ProgressColumn("Trust",     min_value=0, max_value=100, format="%d"),
                    "Readiness": st.column_config.ProgressColumn("Readiness", min_value=0, max_value=100, format="%d"),
                },
            )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Methodology
# ─────────────────────────────────────────────────────────────────────────────

elif page == "Methodology":
    st.markdown("## Scoring Methodology")
    st.markdown('<p style="color:#7AB8F5;margin-top:-12px;margin-bottom:24px;">How the Agentic Retail Readiness score is calculated.</p>', unsafe_allow_html=True)

    # Pillar overview cards
    col_t, col_r = st.columns(2)
    with col_t:
        st.markdown("""
        <div class="sf-card">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
            <span style="background:#0176D3;border-radius:8px;padding:6px 12px;font-size:1.1rem;">🛡</span>
            <span style="font-size:1.05rem;font-weight:800;color:#FFFFFF;">Agentic Trust</span>
            <span class="sf-pill" style="margin-left:auto;">40% weight</span>
          </div>
          <p style="color:#C9E5FF;font-size:0.88rem;line-height:1.6;">
            Can an AI agent <strong>trust</strong> this site? Covers security posture, transparency of policies, and explicit AI-agent signals that indicate the site is safe to interact with on a customer's behalf.
          </p>
        </div>
        """, unsafe_allow_html=True)
    with col_r:
        st.markdown("""
        <div class="sf-card">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
            <span style="background:#04E0A8;color:#032D60;border-radius:8px;padding:6px 12px;font-size:1.1rem;">⚡</span>
            <span style="font-size:1.05rem;font-weight:800;color:#FFFFFF;">Agentic Readiness</span>
            <span class="sf-pill" style="margin-left:auto;">60% weight</span>
          </div>
          <p style="color:#C9E5FF;font-size:0.88rem;line-height:1.6;">
            Can an AI agent <strong>operate</strong> on this site? Covers structured data richness, navigation/search, checkout accessibility, and headless/API architecture signals that enable autonomous actions.
          </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
### Agentic Trust Checks

**Security**
- **HTTPS / TLS** (weight 1.5×) — Agents refuse to operate on insecure origins.
- **Security Headers** (1×) — HSTS, X-Content-Type-Options, X-Frame-Options, CSP signal mature engineering.

**Transparency**
- **Privacy Policy** (1×) — Required for agents handling customer data.
- **Returns Policy** (1×) — Agents need to communicate return terms before purchase delegation.
- **Contact Info** (0.5×) — Customer service reachability signals brand legitimacy.
- **Dark Patterns (absent)** (1×) — Urgency triggers, false scarcity, countdown timers undermine agent trust.

**AI-Specific Signals**
- **robots.txt Present** (0.5×) — Existence of a structured crawl policy.
- **AI Bots Blocked** (1.5×, inverted for Readiness) — GPTBot, ClaudeBot, PerplexityBot disallow rules.
- **llms.txt Present** (2×) — Curated LLM-optimised site summary. Highest trust signal available today.

---

### Agentic Readiness Checks

**Data**
- **Schema.org Markup** (2×) — JSON-LD with Product, Offer, SearchAction types. Correlates 3× with AI citation rates.
- **Product Data Richness** (2×) — Price, availability, SKU/GTIN, ratings, shipping in markup.
- **Sitemap** (1×) — Structured URL index for agent discovery.
- **Performance Hints** (0.5×) — TTFB < 3s, CDN caching, lazy-loading.

**Navigation**
- **On-Site Search** (1.5×) — Search input + optional SearchAction schema. Primary agent navigation method.
- **Clear Navigation** (1×) — Structured nav/header links.
- **Accessibility Basics** (1×) — Alt text, lang attribute, form labels. Agents rely on semantic HTML.

**Checkout**
- **Guest Checkout Signal** (1.5×) — Cart/checkout indicators. Agents cannot create accounts.
- **BNPL / Payment Options** (1×) — Afterpay, Zip, Klarna, PayPal etc. Richer options = more actionable.

**API / Headless**
- **Headless / API Readiness** (1.5×) — Shopify Storefront API, Next.js, GraphQL, API documentation.
- **AI Access Permitted** (2×) — No AI crawler restrictions in robots.txt.
- **Bot HTTP Access** (1.5×) — Site responds correctly to bot user-agent requests.

---

### Grade Scale

| Grade | Score | What it means |
|-------|-------|---------------|
| **A** | 80–100 | Highly agentic-ready. Rich structured data, open AI access, full checkout signals. |
| **B** | 65–79 | Strong foundation. Minor gaps in AI signals or schema coverage. |
| **C** | 50–64 | Partially ready. Missing llms.txt, schema markup, or AI access. |
| **D** | 35–49 | Limited readiness. Functional site but not optimised for agent interaction. |
| **F** | 0–34 | Significant barriers. Blocking crawlers, no structured data, or access failures. |

---

### Limitations
- JavaScript-heavy SPAs may score lower than deserved — checks run on server-rendered HTML only.
- Schema.org checks cover JSON-LD only; Microdata and RDFa are not detected.
- Performance checks are indicative (single-request TTFB), not full Core Web Vitals.
- robots.txt checks cover the homepage; some sites use per-path directives not captured here.
""")
