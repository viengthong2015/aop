"""
AOP 2027 – live data-quality & budget-analysis dashboard (Streamlit, Lao / English).

    streamlit run streamlit_app.py

Re-uses the analysis engine in ./aop_tool (same checks and numbers as the
command-line tool). The source workbook is only ever opened read-only.
"""
from __future__ import annotations

import glob
import hashlib
import json
import math
import os
import re
import sys
import tempfile
import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "aop_tool"))

from i18n import LANGS, Tr  # noqa: E402
from pipeline import CHECKS, SEVERITY_ORDER, Run  # noqa: E402
from report import ISSUE_COLUMNS, LINE_COLUMNS, _layout_doc, write_all  # noqa: E402

st.set_page_config(page_title="AOP 2027", page_icon=":material/monitoring:", layout="wide",
                   initial_sidebar_state="expanded")

# --------------------------------------------------------------------------- language
st.session_state.setdefault("lang", "lo")
with st.sidebar:
    st.segmented_control("ພາສາ / Language", list(LANGS), format_func=LANGS.get, key="lang", width="stretch")
T = Tr(st.session_state.lang or "lo")

# --------------------------------------------------------------------------- UI mode (Default / Crystal)
st.session_state.setdefault("ui_mode", "default")
CRYSTAL = st.session_state.get("ui_mode") == "crystal"
with st.container(key="ui-style-switch"):
    st.segmented_control("UI", ["default", "crystal"], key="ui_mode", label_visibility="collapsed", width="content",
                         format_func={"default": ":material/light_mode: Default",
                                      "crystal": ":material/diamond: Crystal"}.get)

# --------------------------------------------------------------------------- palette (validated per mode)
if not CRYSTAL:   # light mint surface
    INK, SLATE, FOREST = "#14302A", "#5C6470", "#1E7B4F"
    G1 = "#17864F"                                                   # single-series marks
    CAT = ["#1e7b4f", "#2a78d6", "#d4a72c", "#c04f8a", "#eb6834"]   # passes CVD/normal-vision checks in this order
    SEQ = ["#e3f4e9", "#bfe6cd", "#8fd2a8", "#5cb983", "#33a066", "#1e7b4f", "#0b5d3b"]
    OUTLIER = "#eb6834"
    GRID, AXIS, HOVER_BG, HOVER_BORDER = "rgba(20,48,42,.08)", "rgba(20,48,42,.15)", "#ffffff", "#bfe6cd"
    BAND, FILL, RING, MEDIAN = "rgba(30,123,79,.10)", "rgba(23,134,79,.10)", "#ffffff", "#14302A"
else:             # dark emerald surface (#0a2a1e) – validated separately in dark mode
    INK, SLATE, FOREST = "#E8F7EF", "#9FC2B3", "#34D399"
    G1 = "#22B07D"
    CAT = ["#199e70", "#3987e5", "#c98500", "#9085e9", "#d95926"]
    SEQ = ["#0d3a2a", "#0f5138", "#137049", "#199e70", "#34c08a", "#6ee7b7", "#a7f3d0"]
    OUTLIER = "#f08a4b"
    GRID, AXIS, HOVER_BG, HOVER_BORDER = "rgba(209,250,229,.08)", "rgba(209,250,229,.18)", "#062118", "#1f6f50"
    BAND, FILL, RING, MEDIAN = "rgba(52,211,153,.12)", "rgba(52,211,153,.14)", "#0a2a1e", "#d1fae5"
SEV_COLOR = {"Critical": "#d03b3b", "High": "#ec835a", "Medium": "#fab219", "Low": "#898781", "Info": "#2a78d6"}
SEV_ICON = {"Critical": "■", "High": "▲", "Medium": "◆", "Low": "●", "Info": "ℹ"}
LEVEL_COLOR = {"Central": CAT[0], "Province": CAT[1], "District": CAT[2], "Civil society": CAT[3], "Multiple": CAT[4]}
COMP_COLOR = {"Component 1": CAT[0], "Component 2": CAT[1], "Component 3": CAT[2]}
DIMS = ["Reconciliation", "Structure", "Arithmetic", "Completeness", "Validity", "Consistency", "Uniqueness", "Integrity"]
FONT = '"Noto Sans Lao", "Source Sans", "Segoe UI", sans-serif'
MATERIAL = {"Critical", "High", "Medium"}
KIND_LO = {"line": "ລາຍການ", "subtotal": "ຍອດຍ່ອຍ", "heading": "ຫົວຂໍ້", "grand_total": "ຍອດລວມ"}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Lao:wght@400;500;600;700;800&display=swap');
:root {{
  --ink:{INK}; --slate:{SLATE}; --forest:{FOREST}; --rule:#D3DED5;
  --grad: linear-gradient(120deg, #0B5D3B 0%, #17864F 55%, #3DBA74 100%);
}}
html, body, .stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp button, .stApp textarea,
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"] {{ font-family: {FONT}; }}
/* headings, dropdowns, popovers and tooltips: force Noto Sans Lao (keep Material icon glyphs) */
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
[data-baseweb="select"] *:not([data-testid="stIconMaterial"]),
[data-baseweb="popover"] *:not([data-testid="stIconMaterial"]),
[data-baseweb="tooltip"] *:not([data-testid="stIconMaterial"]),
[data-testid="stTooltipContent"] *, [data-testid="stToast"] * {{ font-family: {FONT} !important; }}
.stApp {{
  color: var(--ink);
  background:
    radial-gradient(circle at 8% 0%, rgba(61,186,116,.22), transparent 36%),
    radial-gradient(circle at 92% 6%, rgba(61,186,116,.16), transparent 32%),
    radial-gradient(circle at 50% 100%, rgba(30,123,79,.10), transparent 45%),
    linear-gradient(180deg, #EEF8F1 0%, #E4F3E9 100%);
  background-attachment: fixed;
}}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1400px; }}
[data-testid="stSidebar"] > div:first-child {{
  background: linear-gradient(180deg, rgba(255,255,255,.7), rgba(220,241,228,.6));
  backdrop-filter: blur(18px) saturate(140%); border-right: 1px solid rgba(61,186,116,.25);
}}
/* busy label */
.stApp[data-test-script-state="running" i]::before {{
  content: "{T('busy')}"; position: fixed; top: 1rem; left: 50%; z-index: 999999; transform: translateX(-50%);
  padding: .55rem 1.2rem; border-radius: .35rem; background: var(--ink); color: #fff; font-size: 1rem; font-weight: 600;
  pointer-events: none; font-family: {FONT};
}}
/* masthead */
.masthead {{ margin: .2rem 0 1.2rem; }}
.masthead h1 {{
  margin: 0; padding: 0 0 .15rem; width: fit-content; font-size: clamp(1.8rem, 3.1vw, 2.7rem); font-weight: 800; line-height: 1.2;
  background: var(--grad); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
  font-stretch: 85%; letter-spacing: -.005em;
}}
.masthead p {{ max-width: 80ch; margin: .45rem 0 0; color: var(--slate); font-size: 1.02rem; line-height: 1.6; }}
.masthead .meta {{ font-size: .86rem; color: var(--slate); margin-top: .35rem; }}
/* stepper (main navigation) */
.st-key-step-tabs [data-baseweb="tab-list"] {{
  counter-reset: step; gap: .3rem .5rem !important; padding: .55rem .9rem; border-radius: 16px; flex-wrap: wrap;
  border: 1px solid rgba(120,220,160,.35);
  background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,0)),
              linear-gradient(120deg, #072B1D 0%, #0D4430 50%, #0A3524 100%);
  box-shadow: 0 12px 30px rgba(7,43,29,.35), inset 0 1px 0 rgba(255,255,255,.12);
}}
.st-key-step-tabs button[data-baseweb="tab"] {{
  counter-increment: step; display: flex; align-items: center; gap: .5rem; flex: 0 0 auto;
  padding: .3rem .55rem !important; border-radius: 999px !important; background: transparent !important;
}}
.st-key-step-tabs button[data-baseweb="tab"]::before {{
  content: counter(step); display: inline-grid; place-items: center; width: 28px; height: 28px; flex: none;
  border-radius: 50%; border: 1.5px solid rgba(255,255,255,.55); color: #fff; font-weight: 700; font-size: .9rem;
}}
.st-key-step-tabs button[data-baseweb="tab"] p {{ color: rgba(255,255,255,.78) !important; font-weight: 600; font-size: .98rem; white-space: nowrap; }}
.st-key-step-tabs button[data-baseweb="tab"][aria-selected="true"]::before {{
  background: linear-gradient(135deg, #2BAA63, #4FD08A); border-color: transparent;
  box-shadow: 0 0 0 4px rgba(79,208,138,.22), 0 0 14px rgba(79,208,138,.55);
}}
.st-key-step-tabs button[data-baseweb="tab"][aria-selected="true"] p {{ color: #fff !important; }}
.st-key-step-tabs button[data-baseweb="tab"]:hover p {{ color: #fff !important; }}
.st-key-step-tabs [data-baseweb="tab-highlight"], .st-key-step-tabs [data-baseweb="tab-border"] {{ display: none; }}
/* section header */
.sec {{ display: flex; gap: .9rem; align-items: center; margin: 1.3rem 0 .9rem; }}
.sec .num {{
  width: 46px; height: 46px; flex: none; border-radius: 50%; display: grid; place-items: center; color: #fff;
  font-weight: 800; font-size: 1.15rem; background: radial-gradient(circle at 30% 25%, #4FD08A, #17864F 60%, #0B5D3B);
  box-shadow: 0 6px 16px rgba(23,134,79,.35), inset 0 1px 0 rgba(255,255,255,.35);
}}
.sec h3 {{ margin: 0; padding: 0; font-size: 1.45rem; font-weight: 800; color: var(--ink); font-stretch: 85%; line-height: 1.25; }}
.sec p {{ margin: .15rem 0 0; color: var(--slate); font-size: .93rem; line-height: 1.5; }}
/* glass cards */
[class*="st-key-glass-"] {{
  background: linear-gradient(160deg, rgba(255,255,255,.9), rgba(226,244,233,.74)) !important;
  border: 1px solid rgba(61,186,116,.32) !important; border-radius: 16px !important;
  box-shadow: 0 10px 28px rgba(30,123,79,.12), inset 0 1px 0 rgba(255,255,255,.95);
  padding: 1rem 1.1rem .7rem !important; transition: box-shadow 200ms ease, border-color 200ms ease;
}}
[class*="st-key-glass-"]:hover {{
  border-color: rgba(61,186,116,.55) !important;
  box-shadow: 0 14px 34px rgba(30,123,79,.18), 0 0 16px rgba(61,186,116,.18), inset 0 1px 0 rgba(255,255,255,.95);
}}
.ct {{ font-weight: 700; font-size: 1rem; color: var(--ink); line-height: 1.4; }}
.ct .material {{ color: var(--forest); }}
.cd {{ color: var(--slate); font-size: .86rem; margin: .1rem 0 .3rem; line-height: 1.45; }}
/* sidebar step cards */
[class*="st-key-side-"] {{
  background: linear-gradient(160deg, rgba(255,255,255,.92), rgba(226,244,233,.8)); border: 1px solid rgba(61,186,116,.35);
  border-radius: 14px; padding: .7rem .8rem .55rem; box-shadow: 0 6px 16px rgba(30,123,79,.10);
}}
.sbh {{ display: flex; align-items: center; gap: .55rem; font-weight: 700; color: var(--ink); font-size: .95rem; }}
.sbh .n {{ width: 24px; height: 24px; border-radius: 50%; display: grid; place-items: center; color: #fff; font-size: .8rem;
  background: linear-gradient(135deg, #17864F, #3DBA74); box-shadow: 0 0 0 3px rgba(61,186,116,.18); flex: none; }}
.sb-title {{ font-weight: 800; color: var(--ink); font-size: 1.02rem; margin: .4rem 0 .5rem; }}
.sb-total {{ font-weight: 700; color: var(--forest); }}
/* metric tiles: crystal */
[data-testid="stMetric"] {{
  padding: .75rem 1rem .6rem !important; height: 100%;
  background: linear-gradient(165deg, rgba(255,255,255,.92), rgba(206,238,218,.72)) !important;
  border: 1.5px solid rgba(61,186,116,.6) !important; border-radius: 14px !important;
  box-shadow: 0 8px 22px rgba(30,123,79,.16), 0 0 14px rgba(61,186,116,.28), inset 0 1px 0 rgba(255,255,255,.95);
}}
[data-testid="stMetricLabel"] p {{ white-space: normal !important; font-size: .86rem; color: var(--ink); font-weight: 600; }}
[data-testid="stMetricValue"] {{ font-weight: 800; font-variant-numeric: tabular-nums lining-nums; color: var(--ink);
  font-size: clamp(1.3rem, 1.7vw, 1.7rem) !important; }}
[data-testid="stMetricValue"] p {{ overflow: visible !important; text-overflow: clip !important; }}
[data-testid="stMetricDelta"] p, [data-testid="stMetricLabel"] p {{
  overflow: visible !important; text-overflow: clip !important; white-space: normal !important; }}
[data-testid="stMetricLabel"] [data-testid="stMarkdownContainer"] {{ overflow: visible !important; white-space: normal !important; }}
[data-testid="stBaseButton-segmented_controlActive"] {{
  background: linear-gradient(120deg, #17864F 0%, #2BAA63 60%, #4FD08A 100%) !important; border-color: transparent !important;
  box-shadow: 0 4px 12px rgba(43,170,99,.32), inset 0 1px 0 rgba(255,255,255,.35);
}}
[data-testid="stBaseButton-segmented_controlActive"] p, [data-testid="stBaseButton-segmented_controlActive"] span {{ color: #fff !important; }}
[data-testid="stBaseButton-pillsActive"] {{ background: rgba(61,186,116,.18) !important; border-color: #2BAA63 !important; }}
[data-testid="stMetricDelta"] {{ background: rgba(61,186,116,.16) !important; border-radius: 999px; padding: .1rem .6rem !important; width: fit-content; }}
[data-testid="stMetricDelta"] div {{ white-space: normal !important; font-size: .78rem; color: #1E7B4F !important; }}
.st-key-kpi-hero [data-testid="stMetricValue"] {{ font-size: clamp(1.7rem, 2.3vw, 2.15rem) !important; }}
[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) {{ align-items: stretch; }}
[data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) [data-testid="stElementContainer"]:has(> [data-testid="stMetric"]) {{ height: 100%; }}
/* findings list, dimension cards */
.finding {{ padding: .55rem 0; border-top: 1px solid rgba(20,48,42,.1); }}
.finding:first-child {{ border-top: 0; }}
.finding .t {{ font-weight: 700; color: var(--ink); }}
.finding .m {{ color: var(--slate); font-size: .84rem; }}
.sev {{ font-size: .8rem; white-space: nowrap; font-weight: 600; }}
.dims {{ display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 12px; margin: .2rem 0 1rem; }}
.dimc {{ background: linear-gradient(165deg, rgba(255,255,255,.92), rgba(206,238,218,.72)); border: 1.5px solid rgba(61,186,116,.5);
  border-radius: 14px; padding: .7rem .9rem; box-shadow: 0 8px 22px rgba(30,123,79,.12); }}
.dimc .l {{ font-size: .86rem; font-weight: 600; color: var(--ink); }}
.dimc .v {{ font-size: 1.9rem; font-weight: 800; color: var(--ink); line-height: 1.2; }}
.dimc .n {{ font-size: .76rem; color: var(--slate); margin-top: .3rem; }}
.thin {{ display: flex; height: 6px; border-radius: 999px; overflow: hidden; background: rgba(20,48,42,.08); gap: 2px; margin-top: .4rem; }}
.thin span {{ display: block; height: 100%; }}
.pill {{ display: inline-block; font-size: .78rem; padding: .05rem .6rem; border-radius: 999px; background: rgba(61,186,116,.16); color: #1E7B4F; font-weight: 600; }}
[data-testid="stDataFrame"] {{ border-radius: 12px; overflow: hidden; }}
.stDownloadButton button[kind="primary"], .stButton button[kind="primary"] {{
  background: linear-gradient(120deg, #17864F 0%, #2BAA63 60%, #4FD08A 100%); border: 0;
  box-shadow: 0 4px 14px rgba(43,170,99,.35), inset 0 1px 0 rgba(255,255,255,.35);
}}
@media (max-width: 900px) {{ .dims {{ grid-template-columns: repeat(2, minmax(0,1fr)); }} }}
/* KPI tiles: equal heights per row, no mid-word breaks */
[data-testid="stColumn"] > [data-testid="stVerticalBlock"]:has(> [class*="st-key-kpi-"]) {{ height: 100%; }}
[class*="st-key-kpi-"] {{ height: 100%; position: relative; gap: 0 !important; }}
[class*="st-key-kpi-"] > [data-testid="stElementContainer"]:has([data-testid="stMetric"]) {{ flex: 1 1 auto; }}
[data-testid="stMetricLabel"] p, [data-testid="stMetricDelta"] p {{ word-break: normal !important; overflow-wrap: normal !important; }}
/* clickable KPI tiles: an invisible button covers the whole tile */
[class*="st-key-kpi-click-"] {{ cursor: pointer; }}
[class*="st-key-kpi-click-"] [data-testid="stMetric"] {{ padding-bottom: 2.1rem !important; transition: transform 160ms ease, box-shadow 160ms ease; }}
[class*="st-key-kpi-click-"]:hover [data-testid="stMetric"] {{ transform: translateY(-2px);
  box-shadow: 0 14px 30px rgba(30,123,79,.22), 0 0 20px rgba(61,186,116,.4), inset 0 1px 0 rgba(255,255,255,.95) !important; }}
[class*="st-key-kpi-click-"] > [data-testid="stElementContainer"]:has([data-testid="stButton"]) {{ position: absolute; inset: 0; z-index: 3; margin: 0; }}
[class*="st-key-kpi-click-"] [data-testid="stButton"], [class*="st-key-kpi-click-"] [data-testid="stButton"] button {{
  width: 100%; height: 100%; min-height: 100%; }}
[class*="st-key-kpi-click-"] [data-testid="stButton"] button {{ opacity: 0; cursor: pointer; }}
[class*="st-key-kpi-click-"]::after {{ content: "{T('view_all')}"; position: absolute; right: 16px; bottom: 12px; z-index: 2;
  font-size: .78rem; font-weight: 700; color: var(--forest); pointer-events: none; }}
div[role="dialog"] {{ border-radius: 18px !important; }}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* UI-mode switch: pill in the top bar */
.st-key-ui-style-switch { position: fixed; top: .55rem; right: 8.2rem; z-index: 999991; width: auto !important; }
.st-key-ui-style-switch [data-testid="stButtonGroup"] { padding: 4px; border-radius: 999px; gap: 2px;
  background: rgba(255,255,255,.75); border: 1px solid rgba(61,186,116,.35); box-shadow: 0 6px 18px rgba(30,123,79,.12); }
.st-key-ui-style-switch button { border-radius: 999px !important; border: 0 !important; padding: .3rem 1rem !important; min-height: 2rem; }
.st-key-ui-style-switch button[data-testid="stBaseButton-segmented_control"] { background: transparent !important; }
@media (max-width: 640px) { .st-key-ui-style-switch { right: 4.6rem; } }
</style>
""", unsafe_allow_html=True)

if CRYSTAL:
    st.markdown("""
<style>
:root { --ink:#E8F7EF; --slate:#9FC2B3; --forest:#34D399;
  --grad: linear-gradient(120deg, #4ADE80 0%, #34D399 45%, #2DD4BF 100%); --glass: linear-gradient(155deg, rgba(10,52,37,.62) 0%, rgba(4,25,18,.72) 100%);
  --edge: rgba(52,211,153,.19); --field: rgba(2,19,13,.55); }
.stApp { color: var(--ink);
  background: radial-gradient(circle at 88% 92%, rgba(45,212,191,.13), transparent 40%),
              radial-gradient(circle at 12% 10%, #093526 0%, #041d14 42%, #02130d 100%) !important; background-attachment: fixed; }
[data-testid="stHeader"] { background: rgba(3,22,15,.72) !important; backdrop-filter: blur(10px); }
[data-testid="stHeader"] *, [data-testid="stToolbar"] * { color: #d1fae5 !important; }
[data-testid="stSidebar"] > div:first-child { background: linear-gradient(180deg, #04190f 0%, #02130d 100%) !important;
  border-right: 1px solid rgba(52,211,153,.12); box-shadow: inset -1px 0 0 rgba(209,250,229,.05); }
/* text */
.stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp strong, .stApp b,
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"] p, [data-testid="stMetricLabel"] p,
[data-testid="stMetricValue"], [data-testid="stMetricValue"] p { color: var(--ink) !important; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p, .cd, .sec p, .masthead p, .masthead .meta,
.dimc .n, .finding .m { color: var(--slate) !important; }
.stApp code { background: rgba(2,19,13,.6); color: #a7f3d0; }
/* masthead as a glass card */
.masthead.mh { background: var(--glass); border: 1px solid var(--edge); border-radius: 22px; padding: 1.4rem 1.7rem 1.2rem;
  box-shadow: 0 20px 44px -16px rgba(0,0,0,.65), inset 0 1px 0 rgba(209,250,229,.16); }
.masthead h1 { background: var(--grad); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent !important; }
/* glass cards, sidebar cards, tiles */
[class*="st-key-glass-"], [data-testid="stMetric"], .dimc {
  background: var(--glass) !important; border: 1px solid var(--edge) !important; border-radius: 20px !important;
  box-shadow: 0 20px 44px -16px rgba(0,0,0,.65), inset 0 1px 0 rgba(209,250,229,.16) !important; }
[class*="st-key-glass-"]:hover { border-color: rgba(52,211,153,.42) !important; }
[class*="st-key-side-"] { background: rgba(6,33,24,.62) !important; border: 1px solid var(--edge) !important; box-shadow: none !important; }
.sbh, .sb-title { color: var(--ink) !important; }
.sbh .n { background: transparent !important; border: 1.5px solid #34d399; color: #a7f3d0; box-shadow: none !important; border-radius: 8px; }
.sb-total { color: #6ee7b7 !important; }
[data-testid="stMetricDelta"] { background: rgba(16,185,129,.12) !important; border: 1px solid rgba(52,211,153,.45); }
[data-testid="stMetricDelta"] div, [data-testid="stMetricDelta"] p { color: #6ee7b7 !important; }
.pill { background: rgba(16,185,129,.14); color: #6ee7b7; }
.finding { border-top-color: rgba(209,250,229,.08); }
.thin { background: rgba(209,250,229,.08); }
/* stepper + section badges */
.st-key-step-tabs [data-baseweb="tab-list"] { background: var(--glass) !important; border: 1px solid var(--edge) !important;
  box-shadow: 0 20px 44px -16px rgba(0,0,0,.65), inset 0 1px 0 rgba(209,250,229,.16) !important; }
.st-key-step-tabs button[data-baseweb="tab"][aria-selected="true"]::before { background: linear-gradient(135deg, #10b981, #34d399) !important; }
.sec .num { border-radius: 12px; background: rgba(16,185,129,.12); border: 1.5px solid rgba(52,211,153,.55); color: #d1fae5;
  box-shadow: 0 0 18px rgba(52,211,153,.18); }
/* inputs, selects, menus */
[data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="base-input"], .stTextInput input, [data-testid="stFileUploaderDropzone"] {
  background: var(--field) !important; border-color: rgba(52,211,153,.24) !important; color: var(--ink) !important; }
[data-baseweb="select"] *, .stTextInput input { color: var(--ink) !important; }
[data-baseweb="select"] svg { fill: #9FC2B3 !important; }
[data-baseweb="popover"] ul, [data-baseweb="popover"] [role="listbox"], [data-baseweb="menu"] { background: #062118 !important; }
[data-baseweb="popover"] li { color: var(--ink) !important; }
[data-baseweb="popover"] li:hover, [data-baseweb="popover"] li[aria-selected="true"] { background: rgba(52,211,153,.16) !important; }
/* buttons */
[data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-segmented_control"], [data-testid="stBaseButton-pills"] {
  background: var(--field) !important; border-color: rgba(52,211,153,.24) !important; color: var(--ink) !important; }
[data-testid="stBaseButton-secondary"] *, [data-testid="stBaseButton-segmented_control"] *, [data-testid="stBaseButton-pills"] * { color: var(--ink) !important; }
[data-testid="stBaseButton-segmented_controlActive"] { background: linear-gradient(120deg, #10b981 0%, #34d399 100%) !important; }
[data-testid="stBaseButton-segmented_controlActive"] *, [data-testid="stBaseButton-segmented_controlActive"] p { color: #02130d !important; }
[data-testid="stBaseButton-pillsActive"] { background: rgba(52,211,153,.22) !important; border-color: #34d399 !important; }
/* expanders, alerts */
[data-testid="stExpander"] details { background: rgba(2,19,13,.45) !important; border: 1px solid var(--edge) !important; border-radius: 14px; }
[data-testid="stExpander"] summary * { color: var(--ink) !important; }
[data-testid="stAlert"] > div { background: rgba(16,185,129,.10) !important; border: 1px solid var(--edge); }
/* data tables (canvas grid): invert to a dark grid, keep hues */
[data-testid="stDataFrame"] { filter: invert(.9) hue-rotate(180deg) saturate(1.1); border-radius: 12px; }
/* mode switch on dark */
.st-key-ui-style-switch [data-testid="stButtonGroup"] { background: rgba(2,19,13,.7) !important; border-color: rgba(52,211,153,.3) !important; }
.stApp[data-test-script-state="running" i]::before { background: #10b981 !important; color: #02130d !important; }
div[role="dialog"] { background: #06231a !important; border: 1px solid var(--edge) !important; color: var(--ink); }
div[role="dialog"] p, div[role="dialog"] h2, div[role="dialog"] strong, div[role="dialog"] b, div[role="dialog"] li,
div[role="dialog"] [data-testid="stMarkdownContainer"] { color: var(--ink) !important; }
div[role="dialog"] button[aria-label="Close"] svg { color: var(--ink) !important; }
[class*="st-key-kpi-click-"]:hover [data-testid="stMetric"] { box-shadow: 0 20px 44px -16px rgba(0,0,0,.65), 0 0 22px rgba(52,211,153,.35) !important; border-color: rgba(52,211,153,.5) !important; }
[class*="st-key-kpi-click-"]::after { color: #6ee7b7 !important; }
[data-testid="stTooltipIcon"] svg, [data-testid="stTooltipHoverTarget"] svg { color: #9FC2B3 !important; stroke: #9FC2B3 !important; }
.stApp input::placeholder, .stApp textarea::placeholder { color: rgba(159,194,179,.65) !important; }
[data-testid="stRadio"] [role="radio"] > div:first-child { border-color: rgba(52,211,153,.5) !important; }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------- helpers
def usd(v, full=False):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "–"
    a = abs(v)
    if full:
        return f"${v:,.0f}"
    if a >= 1e6:
        return f"${v / 1e6:.2f}M"
    if a >= 1e3:
        return f"${v / 1e3:.1f}K"
    return f"${v:,.0f}"


def sev_label(s):
    return f"{SEV_ICON.get(s, '')} {T.sev(s)}" if s else "–"


def sec(n, title, desc=""):
    st.markdown(f"<div class='sec'><div class='num'>{n}</div><div><h3>{title}</h3>"
                f"{f'<p>{desc}</p>' if desc else ''}</div></div>", unsafe_allow_html=True)


def card_head(title, desc=""):
    """Card title (markdown, so :material/...: icons render) + muted description."""
    st.markdown(f"**{title}**")
    if desc:
        st.markdown(f"<div class='cd'>{desc}</div>", unsafe_allow_html=True)


def base_layout(fig, h=320, **kw):
    fig.update_layout(height=h, margin=dict(l=6, r=18, t=10, b=8), font=dict(family=FONT, size=12.5, color=INK),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      showlegend=kw.pop("showlegend", False), bargap=kw.pop("bargap", 0.42),
                      hoverlabel=dict(font=dict(family=FONT, color=INK), bgcolor=HOVER_BG, bordercolor=HOVER_BORDER), **kw)
    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False, linecolor=AXIS)
    fig.update_yaxes(showgrid=False, zeroline=False)
    return fig


_CHART_IDS = iter(range(10 ** 6))  # module re-runs on every rerun -> stable, unique keys


def chart(fig, key=None, on_select="ignore"):
    key = key or f"chart_{next(_CHART_IDS)}"
    return st.plotly_chart(fig, width="stretch", key=key, on_select=on_select,
                           config={"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]})


def hbar(labels, values, custom=None, hover="<b>%{y}</b><br>%{x:$,.0f}<extra></extra>", h=None):
    fig = go.Figure(go.Bar(x=values, y=labels, orientation="h", marker=dict(color=G1, cornerradius=4),
                           text=[usd(v) for v in values], textposition="outside", cliponaxis=False,
                           customdata=custom, hovertemplate=hover, textfont=dict(size=11.5, color=INK),
                           constraintext="none"))
    base_layout(fig, h=h or max(260, 27 * len(labels) + 30))
    fig.update_xaxes(range=[0, (max(values) if len(values) else 1) * 1.18], tickformat="$.2s")
    return fig


def log_ticks(lo, hi):
    vals = list(range(math.floor(lo), math.ceil(hi) + 1))
    txt = [("$" + (f"{10 ** e / 1e6:g}M" if e >= 6 else f"{10 ** e / 1e3:g}K" if e >= 3 else f"{10 ** e:g}")) for e in vals]
    return vals, txt


def file_sig(path):
    s = os.stat(path)
    return s.st_mtime, s.st_size


@st.cache_data(show_spinner=False, max_entries=6)
def analyse(path: str, mtime: float, size: int) -> dict:
    """Run the full pipeline once per (file, version). Returns plain, cacheable data."""
    before = file_sig(path)
    t0 = time.time()
    run = Run(path).run()
    with tempfile.TemporaryDirectory() as td:
        files, qs = write_all(run, td)
        blobs = {k: open(v, "rb").read() for k, v in files.items()}
    if file_sig(path) != before:
        raise RuntimeError("Source workbook changed during analysis – please re-run.")
    recs = [{k: v for k, v in r.items() if not k.startswith("_")} for r in run.records]
    port = [r for r in recs if r["in_portfolio"]]
    return dict(
        records=recs, issues=run.issues, versions=run.versions, summary_recon=run.summary_recon,
        fx=run.fx, external_links=run.external_links, outliers=run.outlier_rows,
        uc_stats=run.uc_stats, total_stats=getattr(run, "total_stats", None), profile=run.profile_rows,
        sheets=run.sheet_rows, quality=qs, files=blobs,
        meta=dict(source=os.path.basename(path), analysed=time.strftime("%Y-%m-%d %H:%M:%S"),
                  modified=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime)),
                  seconds=round(time.time() - t0, 1), counted_total=sum(r["budget_total"] or 0 for r in port),
                  counted_lines=len(port), parsed_rows=len(recs), sheets_total=len(run.wb.wf.worksheets),
                  hidden=[ws.title for ws in run.wb.wf.worksheets if ws.sheet_state != "visible"]),
        layouts=json.loads(json.dumps(_layout_doc(), default=str)),
    )


def save_upload(up) -> str:
    """Uploaded files are copied to a private temp folder (keeps the original name)."""
    digest = hashlib.sha1(up.getvalue()).hexdigest()[:12]
    d = os.path.join(tempfile.gettempdir(), "aop_streamlit_uploads", digest)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, os.path.basename(up.name))
    if not os.path.exists(p):
        with open(p, "wb") as fh:
            fh.write(up.getvalue())
    return p


def synced(fn, container, label, options, key, **kw):
    """A widget whose translated option labels refresh on a language switch while its value is kept.

    The value lives in st.session_state[key]; each language gets its own widget key."""
    wk = f"{key}__{T.lang}"
    if key in st.session_state:
        st.session_state[wk] = st.session_state[key]
        kw.pop("default", None)

    def _sync():
        st.session_state[key] = st.session_state[wk]
    out = getattr(container, fn)(label, options, key=wk, on_change=_sync, **kw)
    st.session_state[key] = out
    return out


def side_card(n, title, key):
    c = st.sidebar.container(key=f"side-{key}")
    c.markdown(f"<div class='sbh'><span class='n'>{n}</span>{title}</div>", unsafe_allow_html=True)
    return c


# --------------------------------------------------------------------------- sidebar: source + live
st.sidebar.markdown(f"<div class='sb-title'>{T('sb_head')}</div>", unsafe_allow_html=True)
c_src = side_card(1, T("sb_workbook"), "src")
src_mode = synced("radio", c_src, T("sb_workbook"), ["folder", "upload"], "src_mode", horizontal=True,
                  label_visibility="collapsed", format_func=lambda m: T("src_folder") if m == "folder" else T("src_upload"))
path = None
if src_mode == "folder":
    cands = sorted(glob.glob(os.path.join(HERE, "data", "*.xlsx")) + glob.glob(os.path.join(HERE, "data", "*.xlsm")),
                   key=os.path.getmtime, reverse=True)
    cands = [c for c in cands if not os.path.basename(c).startswith("~$")]
    if cands:
        path = c_src.selectbox(T("pick_wb"), cands, format_func=os.path.basename, key="wb_path")
    else:
        c_src.warning(T("no_xlsx"))
else:
    up = c_src.file_uploader(T("upload_wb"), type=["xlsx", "xlsm"])
    if up is not None:
        path = save_upload(up)

st.markdown(f"<div class='masthead mh'><h1>{T('app_title')}</h1><p>{T('app_sub')}</p></div>", unsafe_allow_html=True)
if not path:
    st.info(T("choose_wb"))
    st.stop()

c_live = side_card(2, T("sb_live"), "live")
if c_live.button(T("reanalyse"), icon=":material/refresh:", width="stretch", help=T("reanalyse_help")):
    analyse.clear()
watch = c_live.toggle(T("watch"), value=False, help=T("watch_help"), key="watch")

mtime, size = file_sig(path)
with st.spinner(T("analysing", f=os.path.basename(path))):
    try:
        A = analyse(path, mtime, size)
    except Exception as e:  # pragma: no cover
        st.error(str(e))
        st.stop()
M = A["meta"]


@st.fragment(run_every="5s" if watch else None)
def watcher():
    if watch and os.path.exists(path) and file_sig(path) != (mtime, size):
        st.toast(T("changed"), icon=":material/sync:")
        st.rerun(scope="app")
    if watch:
        st.caption(f":material/visibility: {T('watching')} {time.strftime('%H:%M:%S')}")


with c_live:  # fragments may only write to the sidebar from inside its block
    watcher()
c_live.caption(f"**{M['source']}**  \n" + T("status", m=M["modified"], a=M["analysed"], s=M["seconds"]))

# --------------------------------------------------------------------------- frames
DF = pd.DataFrame(A["records"])
for _c in ["unit_cost_usd", "unit_cost_lak", "quantity", "mov_q1", "mov_q2", "mov_q3", "mov_q4", "mov_total",
           "budget_q1", "budget_q2", "budget_q3", "budget_q4", "budget_total", "quarterly_sum", "total_lak",
           "level", "depth", "issue_count"]:
    DF[_c] = pd.to_numeric(DF[_c], errors="coerce")
DF["material"] = DF["max_severity"].isin(MATERIAL)
DF["_search"] = (DF[["code", "name", "name_alt", "ia_raw", "implementing_agency", "activity_type_raw", "sheet",
                     "sheet_label"]].astype(str).agg(" ".join, axis=1).str.lower())
ISS = pd.DataFrame(A["issues"])
OUT = pd.DataFrame(A["outliers"])
SHEETS = pd.DataFrame(A["sheets"])
SHORT = dict(zip(SHEETS["sheet"], SHEETS["short"]))
LABEL = {s: T.plan(s, l) for s, l in zip(SHEETS["sheet"], SHEETS["label"])}
COUNTED = DF[DF["in_portfolio"]]
ISS_BY_UID = {u: g for u, g in ISS[ISS["uid"].notna()].groupby("uid")} if len(ISS) else {}
OUT_BY_UID = {u: g for u, g in OUT.groupby("uid")} if len(OUT) else {}
CHK = {k: T.check(k, v[1], v[3]) for k, v in CHECKS.items()}   # id -> (title, explanation) in UI language
METRIC = {"Unit cost (USD)": T("m_uc"), "Line total (USD)": T("m_tot"), "Quarterly phasing": T("m_phase")}


def excl_label(x):
    if not x or T.lang == "en":
        return x
    if x == "alternate-language copy":
        return "ສະບັບແປພາສາ"
    if x == "hidden older version":
        return "ສະບັບເກົ່າທີ່ເຊື່ອງໄວ້"
    if x.startswith("duplicate of sheet"):
        return "ຊ້ຳກັບແຜ່ນ " + x.split("sheet ", 1)[1]
    if x.endswith(" row"):
        return "ແຖວ" + KIND_LO.get(x[:-4], x[:-4])
    return x


# --------------------------------------------------------------------------- sidebar: filters
c_f = side_card(3, T("sb_filters"), "filters")
plans = SHEETS[SHEETS["counted_lines"] > 0]["sheet"].tolist()
DEFAULTS = dict(f_sheet="", f_comp="", f_cat="", f_level="", f_qual="all", f_q="")
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)


def reset_filters():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v


synced("selectbox", c_f, T("f_sheet"), [""] + plans, "f_sheet",
       format_func=lambda s: T("all_plans") if not s else f"{SHORT[s]} — {LABEL[s]}")
synced("selectbox", c_f, T("f_comp"), [""] + sorted(COUNTED["component"].dropna().unique()), "f_comp",
       format_func=lambda s: T.comp(s) if s else T("all_comp"))
synced("selectbox", c_f, T("f_cat"), [""] + sorted(COUNTED["activity_category"].dropna().unique()), "f_cat",
       format_func=lambda s: T.cat(s) if s else T("all_cat"))
synced("selectbox", c_f, T("f_level"), [""] + sorted(COUNTED["implementation_level"].dropna().unique()), "f_level",
       format_func=lambda s: T.level(s) if s else T("all_level"))
synced("selectbox", c_f, T("f_qual"), ["all", "issues", "clean", "outlier"], "f_qual",
       format_func=lambda s: T({"all": "q_all", "issues": "q_issues", "clean": "q_clean", "outlier": "q_outlier"}[s]))
c_f.text_input(T("f_q"), key="f_q", placeholder=T("f_q_ph"))
c_f.button(T("reset"), on_click=reset_filters, width="stretch", icon=":material/filter_alt_off:")


def apply_filters(df):
    s = st.session_state
    m = pd.Series(True, index=df.index)
    if s.f_sheet:
        m &= df["sheet"] == s.f_sheet
    if s.f_comp:
        m &= df["component"] == s.f_comp
    if s.f_cat:
        m &= df["activity_category"] == s.f_cat
    if s.f_level:
        m &= df["implementation_level"] == s.f_level
    if s.f_qual == "issues":
        m &= df["material"]
    elif s.f_qual == "clean":
        m &= ~df["material"]
    elif s.f_qual == "outlier":
        m &= df["outlier_flags"].fillna("") != ""
    if s.f_q.strip():
        m &= df["_search"].str.contains(s.f_q.strip().lower(), regex=False)
    return df[m]


L = apply_filters(COUNTED)
filtered = len(L) != len(COUNTED)
c_f.markdown(f"<div class='sb-total'>{T('lines_total', n=f'{len(L):,}', v=usd(L['budget_total'].sum(), True))}</div>",
             unsafe_allow_html=True)


# --------------------------------------------------------------------------- tables & detail
def money(label):
    return st.column_config.NumberColumn(label, format="dollar")


LINE_CFG = {
    "plan": T("col_plan"), "excel_row": st.column_config.NumberColumn(T("col_row"), format="%d"),
    "code": T("col_code"), "name": st.column_config.TextColumn(T("col_activity"), width="large"),
    "activity_category": T("col_cat"), "unit_cost_usd": money(T("col_uc")),
    "quantity": st.column_config.NumberColumn(T("col_qty"), format="localized"),
    **{f"budget_q{i}": money(f"Q{i}") for i in range(1, 5)}, "budget_total": money(T("col_total")),
    "implementing_agency": T("col_agency"), "max_severity": T("col_worst"),
    "issue_count": st.column_config.NumberColumn(T("col_issues"), format="%d"),
    "row_kind": T("col_kind"), "exclusion_reason": T("col_excl"),
}


def to_csv(df, cols=None):
    if cols:
        df = df[[k for k, _ in cols if k in df.columns]].rename(columns=dict(cols))
    return df.to_csv(index=False).encode("utf-8-sig")


def line_details(r):
    """Detail card for one budget line: all fields + issues + outlier flags."""
    with st.container(key=f"glass-detail-{r['uid']}"):
        st.markdown(f"<div class='ct'>{r['code'] or ''} {r['name'] or ''}</div>"
                    f"<div class='cd'>{r['sheet']} · {T('d_row')} {r['excel_row']} · "
                    f"{T('d_counted') if r['in_portfolio'] else T('d_notcounted') + ' — ' + str(excl_label(r['exclusion_reason']))}</div>",
                    unsafe_allow_html=True)
        if r.get("name_alt"):
            st.caption(r["name_alt"])
        a, b, c = st.columns(3)
        a.markdown(f"**{T('d_plan')}** {LABEL.get(r['sheet'], r['sheet_label'])}  \n"
                   f"**{T('d_cat')}** {T.cat(r['activity_category'])}  \n"
                   f"**{T('d_typed')}** {r['activity_type_raw'] or '–'}  \n"
                   f"**{T('d_unit')}** {r['unit_raw'] or '–'} → {r['unit'] or '–'}")
        qty = "–" if pd.isna(r["quantity"]) else f"{r['quantity']:g}"
        movs = " / ".join("–" if pd.isna(r[f"mov_q{i}"]) else f"{r[f'mov_q{i}']:g}" for i in range(1, 5))
        buds = " / ".join(usd(r[f"budget_q{i}"]) for i in range(1, 5))
        b.markdown(f"**{T('d_uc')}** {usd(r['unit_cost_usd'], True)}  \n**{T('d_qty')}** {qty}  \n"
                   f"**{T('d_mov')}** {movs}  \n**{T('d_bud')}** {buds}")
        c.markdown(f"**{T('d_total')} {usd(r['budget_total'], True)}**  \n"
                   f"**{T('d_formula')}** `{r['total_formula'] or T('d_typed_val')}`  \n"
                   f"**{T('d_agency')}** {r['ia_raw'] or '–'} → {T.agency(r['implementing_agency']) or '–'}  \n"
                   f"**{T('d_level')}** {T.level(r['implementation_level']) or '–'}")
        iss = ISS_BY_UID.get(r["uid"])
        if iss is not None:
            st.markdown(f"**{T('d_issues')}**")
            for _, i in iss.iterrows():
                st.markdown(f"<span style='color:{SEV_COLOR[i['severity']]}'>{SEV_ICON[i['severity']]}</span> "
                            f"**{T.sev(i['severity'])}** · `{i['check_id']}` {CHK[i['check_id']][0]} — "
                            f"<span style='color:{SLATE}'>{i['message']}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f":material/check_circle: {T('d_noissue')}")
        o = OUT_BY_UID.get(r["uid"])
        if o is not None:
            for _, x in o.iterrows():
                st.markdown(f":material/scatter_plot: **{T('d_outlier')} – {METRIC.get(x['metric'], x['metric'])}**: "
                            f"{x['direction']} · {T('d_value')} {usd(x['value'], True)}"
                            + (f" · {T('d_peer')} {usd(x['peer_median'], True)} ({T.cat(x['peer_group'])})"
                               if pd.notna(x['peer_median']) else ""))


def selectable_lines(df, key, cols, height=480):
    show = df[cols].copy()
    if "sheet" in show:
        show.insert(0, "plan", show["sheet"].map(SHORT))
        show = show.drop(columns=["sheet"])
    if "max_severity" in show:
        show["max_severity"] = show["max_severity"].map(sev_label)
    if "activity_category" in show:
        show["activity_category"] = show["activity_category"].map(T.cat)
    if "implementing_agency" in show:
        show["implementing_agency"] = show["implementing_agency"].map(T.agency)
    if "row_kind" in show and T.lang == "lo":
        show["row_kind"] = show["row_kind"].map(lambda k: KIND_LO.get(k, k))
    if "exclusion_reason" in show:
        show["exclusion_reason"] = show["exclusion_reason"].map(excl_label)
    for c in show.columns:
        if show[c].dtype == object:
            show[c] = show[c].fillna("–")
    ev = st.dataframe(show, hide_index=True, width="stretch", height=height, on_select="rerun",
                      selection_mode="single-row", key=key, column_config=LINE_CFG)
    rows = ev.selection.rows if ev and ev.selection else []
    if rows:
        line_details(df.iloc[rows[0]])
    else:
        st.caption(T("select_hint"))


# --------------------------------------------------------------------------- main
st.markdown(f"<div class='masthead' style='margin-top:-.8rem'><div class='meta'>📄 <b>{M['source']}</b> · "
            f"{M['sheets_total']} sheets · {M['parsed_rows']} rows · {M['counted_lines']} ✓</div></div>",
            unsafe_allow_html=True)
TAB_KEYS = ["t_overview", "t_quality", "t_outliers", "t_explore", "t_table", "t_structure", "t_export"]
tabs = st.tabs([T(k) for k in TAB_KEYS], key="step-tabs")

# --------------------------------------------------------------------------- KPI drill-down dialogs
def _norm(s):
    return re.sub(r"\W+", "", (s or "").lower())


def dup_groups():
    """Rebuild the U3/U4 duplicate groups exactly as the pipeline defines them."""
    flagged = ISS[ISS["check_id"].isin(["U3", "U4"])]
    groups = []
    for chk in ("U3", "U4"):
        sub = COUNTED[COUNTED["uid"].isin(set(flagged.loc[flagged["check_id"] == chk, "uid"]))]
        if sub.empty:
            continue
        keys = [sub["name"].map(_norm), sub["budget_total"].round()] if chk == "U3" else \
               [sub["budget_total"].round(), sub["activity_category"]]
        for _, g in sub.groupby(keys):
            if g["sheet"].nunique() > 1:
                amt = float(g["budget_total"].max())
                groups.append(dict(check=chk, amount=amt, at_risk=float(g["budget_total"].sum() - amt),
                                   category=g["activity_category"].iloc[0], lines=g, uids=set(g["uid"])))
    return sorted(groups, key=lambda g: -g["at_risk"])


def issue_table(df, key):
    show = df[["severity", "check_id", "sheet", "row", "code", "name", "message"]].copy()
    show.insert(2, "title", df["check_id"].map(lambda c: CHK[c][0]))
    show["severity"] = show["severity"].map(sev_label)
    show[["code", "name"]] = show[["code", "name"]].fillna("–")
    return st.dataframe(show, hide_index=True, width="stretch", height=min(420, 38 + 35 * len(show)), on_select="rerun",
                        selection_mode="single-row", key=key,
                        column_config={"severity": T("severity"), "check_id": T("check"),
                                       "title": st.column_config.TextColumn(T("col_desc"), width="medium"),
                                       "sheet": T("col_sheet"), "row": st.column_config.NumberColumn(T("col_row"), format="%d"),
                                       "code": T("col_code"), "name": st.column_config.TextColumn(T("col_activity"), width="medium"),
                                       "message": st.column_config.TextColumn(T("col_detail"), width="large")})


@st.dialog(T("dlg_crit"), width="large")
def dlg_critical(on_lines, wb_level, n_lines):
    st.markdown(f"<div class='cd'>{T('dlg_crit_d', n=len(on_lines), l=n_lines, w=len(wb_level))}</div>",
                unsafe_allow_html=True)
    both = pd.concat([on_lines, wb_level])
    if len(both):
        by = (both.assign(o=both["severity"].map(SEVERITY_ORDER.index)).groupby("check_id")
              .agg(o=("o", "min"), n=("issue_id", "size"), sev=("severity", "first")).sort_values(["o", "n"], ascending=[True, False]))
        st.markdown(" ".join(f"<span class='pill' style='margin:0 .3rem .35rem 0'>"
                             f"<span style='color:{SEV_COLOR[r.sev]}'>{SEV_ICON[r.sev]}</span> {cid} · {CHK[cid][0]} · {r.n}×</span>"
                             for cid, r in by.iterrows()), unsafe_allow_html=True)
    t1, t2 = st.tabs([f"{T('dlg_on_lines')} ({len(on_lines)})", f"{T('dlg_wb')} ({len(wb_level)})"])
    with t1:
        if on_lines.empty:
            st.caption(T("no_items"))
        else:
            ol = on_lines.assign(_o=on_lines["severity"].map(SEVERITY_ORDER.index)).sort_values(
                ["_o", "check_id", "sheet", "row"])
            ev = issue_table(ol, "dlg_crit_lines")
            if ev.selection.rows:
                line_details(DF[DF["uid"] == ol.iloc[ev.selection.rows[0]]["uid"]].iloc[0])
            else:
                st.caption(T("select_hint"))
    with t2:
        if wb_level.empty:
            st.caption(T("no_items"))
        else:
            issue_table(wb_level, "dlg_crit_wb")
            for _, i in wb_level.iterrows():
                st.markdown(f"<div class='finding'><span class='sev' style='color:{SEV_COLOR[i['severity']]}'>"
                            f"{SEV_ICON[i['severity']]} {T.sev(i['severity'])}</span> <span class='pill'>{i['check_id']}</span>"
                            f"<div class='t'>{CHK[i['check_id']][0]} — {i['sheet']}</div>"
                            f"<div class='m'>{CHK[i['check_id']][1]}</div><div class='m'>{i['message']}</div></div>",
                            unsafe_allow_html=True)
    st.download_button(T("dl_csv"), to_csv(both, ISSUE_COLUMNS), "AOP2027_critical_high_findings.csv", "text/csv",
                       icon=":material/download:", type="primary")


@st.dialog(T("dlg_dup"), width="large")
def dlg_duplicates(groups, at_risk):
    st.markdown(f"<div class='cd'>{T('dlg_dup_d', g=len(groups), v=usd(at_risk, True))}</div>", unsafe_allow_html=True)
    if not groups:
        st.caption(T("no_items"))
        return
    rows = []
    for gi, g in enumerate(groups, 1):
        with st.container(key=f"glass-dup-{gi}"):
            label = T("dup_u3") if g["check"] == "U3" else T("dup_u4")
            st.markdown(f"**{T('group')} {gi}** · <span class='pill'>{g['check']}</span> {label} · "
                        f"{T.cat(g['category'])} · <b>{usd(g['amount'], True)}</b> × {len(g['lines'])} · "
                        f"<span style='color:{OUTLIER}'>{T('at_risk')} {usd(g['at_risk'], True)}</span>",
                        unsafe_allow_html=True)
            gl = g["lines"].assign(plan=g["lines"]["sheet"].map(SHORT),
                                   agency=g["lines"]["implementing_agency"].map(T.agency).fillna(g["lines"]["ia_raw"]))
            st.dataframe(gl[["plan", "sheet", "excel_row", "code", "name", "budget_total", "agency"]], hide_index=True,
                         width="stretch",
                         column_config={"plan": T("col_plan"), "sheet": T("col_sheet"),
                                        "excel_row": st.column_config.NumberColumn(T("col_row"), format="%d"),
                                        "code": T("col_code"), "name": st.column_config.TextColumn(T("col_activity"), width="large"),
                                        "budget_total": money(T("col_total")), "agency": T("col_agency")})
            for _, r in gl.iterrows():
                rows.append(dict(group=gi, check=g["check"], amount_at_risk=g["at_risk"], sheet=r["sheet"],
                                 excel_row=r["excel_row"], code=r["code"], name=r["name"], budget_total=r["budget_total"],
                                 implementing_agency=r["implementing_agency"] or r["ia_raw"]))
    st.download_button(T("dl_csv"), to_csv(pd.DataFrame(rows)), "AOP2027_possible_double_budgeting.csv", "text/csv",
                       icon=":material/download:", type="primary")


# =========================================================================== 1 OVERVIEW
with tabs[0]:
    sec(1, T("ov_title"), T("ov_desc"))
    tot = L["budget_total"].sum()
    CRIT_LINES = ISS[ISS["severity"].isin(["Critical", "High"]) & ISS["uid"].isin(set(L["uid"]))]
    CRIT_WB = ISS[ISS["severity"].isin(["Critical", "High"]) & ISS["uid"].isna() & ~ISS["role"].isin(["superseded", "alternate"])]
    DUP_GROUPS = [g for g in dup_groups() if g["uids"] & set(L["uid"])]
    dup = sum(g["at_risk"] for g in DUP_GROUPS)
    crit = len(CRIT_LINES)
    clean = int((~L["material"]).sum())

    row1 = st.columns([1.4, 1, 1])
    with row1[0], st.container(key="kpi-hero"):
        st.metric(f":material/payments: {T('k_budget_sel') if filtered else T('k_budget')}", usd(tot), usd(tot, True),
                  delta_arrow="off", border=True, help=T("k_budget_help"))
    with row1[1], st.container(key="kpi-lines"):
        st.metric(f":material/table_rows: {T('k_lines')}", f"{len(L):,}", T("k_lines_d", n=M["parsed_rows"]),
                  delta_arrow="off", border=True)
    with row1[2], st.container(key="kpi-plans"):
        st.metric(f":material/folder_open: {T('k_plans')}", L["sheet"].nunique(), T("k_plans_d", n=M["sheets_total"]),
                  delta_arrow="off", border=True)
    row2 = st.columns(3)
    with row2[0], st.container(key="kpi-clean"):
        st.metric(f":material/verified: {T('k_clean')}", f"{100 * clean / max(1, len(L)):.0f}%",
                  T("k_clean_d", c=clean, n=len(L)), delta_arrow="off", border=True)
    with row2[1], st.container(key="kpi-click-crit"):        # whole tile is clickable
        st.metric(f":material/report: {T('k_crit')}", crit, T("k_crit_d"), delta_arrow="off", border=True)
        if st.button(T("view_all"), key="open_crit", width="stretch"):
            dlg_critical(CRIT_LINES, CRIT_WB, len(L))
    with row2[2], st.container(key="kpi-click-dup"):
        st.metric(f":material/content_copy: {T('k_dup')}", usd(dup), T("k_dup_d", g=len(DUP_GROUPS)),
                  delta_arrow="off", border=True)
        if st.button(T("view_all"), key="open_dup", width="stretch"):
            dlg_duplicates(DUP_GROUPS, dup)

    left, right = st.columns([1.25, 1])
    with left, st.container(key="glass-plan"):
        card_head(f":material/bar_chart: {T('c_plan')}", T("c_plan_d"))
        g = L.groupby("sheet").agg(v=("budget_total", "sum"), n=("uid", "size")).sort_values("v")
        fig = hbar([SHORT[s] for s in g.index], g["v"].tolist(), custom=[[LABEL[s], n, s] for s, n in zip(g.index, g["n"])],
                   hover="<b>%{customdata[0]}</b><br>%{x:$,.0f}<br>%{customdata[1]} " + T("hv_lines") + "<extra></extra>")

        def on_plan_click():
            try:
                pts = st.session_state.plan_chart.selection.points
            except Exception:
                pts = []
            if pts:
                sheet = (pts[0].get("customdata") or [None, None, None])[2]
                st.session_state.f_sheet = "" if st.session_state.f_sheet == sheet else sheet
        chart(fig, key="plan_chart", on_select=on_plan_click)
    with right:
        with st.container(key="glass-quarter"):
            card_head(f":material/calendar_month: {T('c_quarter')}", T("c_quarter_d"))
            q = [L[f"budget_q{i}"].sum() for i in range(1, 5)]
            qt = sum(q) or 1
            fig = go.Figure(go.Bar(x=["Q1", "Q2", "Q3", "Q4"], y=q, marker=dict(color=G1, cornerradius=5), width=0.36,
                                   text=[f"{100 * v / qt:.0f}%" for v in q], textposition="outside", cliponaxis=False,
                                   textfont=dict(color=INK), hovertemplate="%{x}: %{y:$,.0f}<extra></extra>"))
            base_layout(fig, h=215)
            fig.update_yaxes(showgrid=True, gridcolor=GRID, tickformat="$.2s")
            fig.update_xaxes(showgrid=False)
            chart(fig)
        with st.container(key="glass-comp"):
            card_head(f":material/donut_large: {T('c_comp')}", T("c_comp_d"))
            for col, cmap, title, tr in [("component", COMP_COLOR, T("c_comp_1"), T.comp),
                                         ("implementation_level", LEVEL_COLOR, T("c_comp_2"), T.level)]:
                g = L.groupby(L[col].fillna("(blank)"))["budget_total"].sum().sort_values(ascending=False)
                fig = go.Figure()
                for name, v in g.items():
                    fig.add_trace(go.Bar(x=[v], y=[title], orientation="h", name=tr(name),
                                         marker=dict(color=cmap.get(name, "#8a9a92"), line=dict(color=RING, width=2)),
                                         text=f"{100 * v / max(1, g.sum()):.0f}%" if v / max(1, g.sum()) > .06 else "",
                                         textposition="inside", insidetextanchor="start",
                                         textfont=dict(color="#0b0b0b" if cmap.get(name) == CAT[2] else "#ffffff"),
                                         hovertemplate=f"<b>{tr(name)}</b><br>%{{x:$,.0f}}<extra></extra>"))
                base_layout(fig, h=105, barmode="stack", showlegend=True, bargap=0.15,
                            legend=dict(orientation="h", y=-0.4, x=0, font=dict(size=11.5), traceorder="normal"))
                fig.update_xaxes(visible=False)
                fig.update_yaxes(visible=False)
                st.caption(title)
                chart(fig)

    left, right = st.columns(2)
    with left, st.container(key="glass-cat"):
        card_head(f":material/category: {T('c_cat')}", T("c_cat_d"))
        g = L.groupby("activity_category").agg(v=("budget_total", "sum"), n=("uid", "size")).sort_values("v")
        chart(hbar([T.cat(c) for c in g.index], g["v"].tolist(), custom=g["n"].tolist(),
                   hover="<b>%{y}</b><br>%{x:$,.0f} · %{customdata} " + T("hv_lines") + "<extra></extra>"))
    with right, st.container(key="glass-find"):
        card_head(f":material/fact_check: {T('c_find')}", T("c_find_d"))
        top = ISS[ISS["severity"].isin(["Critical", "High"]) & ~ISS["role"].isin(["superseded", "alternate"])]
        order = (top.assign(o=top["severity"].map(SEVERITY_ORDER.index)).groupby("check_id")
                 .agg(o=("o", "min"), n=("issue_id", "size")).sort_values(["o", "n"], ascending=[True, False]))
        html = ""
        for cid, row in order.head(9).iterrows():
            ex = top[top["check_id"] == cid].iloc[0]
            sheets = sorted({SHORT.get(s, s) for s in top[top["check_id"] == cid]["sheet"]})
            html += (f"<div class='finding'><span class='sev' style='color:{SEV_COLOR[ex['severity']]}'>"
                     f"{SEV_ICON[ex['severity']]} {T.sev(ex['severity'])}</span> <span class='pill'>{cid} · {row['n']}×</span>"
                     f"<div class='t'>{CHK[cid][0]}</div><div class='m'>{ex['message']}</div>"
                     f"<div class='m'>{', '.join(sheets[:6])}</div></div>")
        st.markdown(html, unsafe_allow_html=True)

# =========================================================================== 2 DATA QUALITY
with tabs[1]:
    sec(2, T("dq_title"), T("dq_desc", n=f"{len(ISS):,}", c=len(CHECKS), p=A["quality"]["clean_pct"]))
    cards = ""
    for d in DIMS:
        sub = ISS[ISS["dimension"] == d]["severity"].value_counts()
        n = int(sub.sum()) or 1
        bar = "".join(f"<span style='width:{100 * sub[s] / n}%;background:{SEV_COLOR[s]}'></span>" for s in SEVERITY_ORDER if s in sub)
        txt = " · ".join(f"{SEV_ICON[s]} {int(sub[s])} {T.sev(s)}" for s in SEVERITY_ORDER if s in sub) or "–"
        cards += (f"<div class='dimc'><div class='l'>{T.dim(d)}</div><div class='v'>{int(sub.sum())}</div>"
                  f"<div class='thin'>{bar}</div><div class='n'>{txt}</div></div>")
    st.markdown(f"<div class='dims'>{cards}</div>", unsafe_allow_html=True)

    left, right = st.columns([1.25, 1])
    with left, st.container(key="glass-heat"):
        card_head(f":material/grid_on: {T('dq_heat')}", T("dq_heat_d"))
        pv = ISS.pivot_table(index="sheet", columns="dimension", values="issue_id", aggfunc="count", fill_value=0)
        pv = pv.reindex(columns=DIMS, fill_value=0)
        pv = pv.loc[pv.sum(axis=1).sort_values().index]
        z = pv.values.astype(float)
        zs = [[((v / max(1, z.max())) ** 0.6) if v > 0 else None for v in row] for row in z]
        fig = go.Figure(go.Heatmap(z=zs, zmin=0, zmax=1, x=[T.dim(d) for d in DIMS], y=[SHORT.get(s, s) for s in pv.index],
                                   text=[[str(int(v)) if v else "" for v in row] for row in z], texttemplate="%{text}",
                                   customdata=z, xgap=3, ygap=3, colorscale=[[i / 6, c] for i, c in enumerate(SEQ)],
                                   showscale=False, textfont=dict(size=11),
                                   hovertemplate="<b>%{y}</b><br>%{x}: %{customdata:.0f}<extra></extra>"))
        base_layout(fig, h=max(320, 23 * len(pv) + 60))
        fig.update_xaxes(showgrid=False, side="top", tickangle=-35, tickfont=dict(size=11))
        chart(fig)
    with right, st.container(key="glass-checks"):
        card_head(f":material/checklist: {T('dq_checks')}")
        g = ISS.groupby("check_id").size().sort_values().tail(14)
        fig = go.Figure(go.Bar(x=g.values, y=[f"{k} · {CHK[k][0][:34]}" for k in g.index], orientation="h",
                               marker=dict(color=G1, cornerradius=4), text=g.values, textposition="outside",
                               cliponaxis=False, customdata=[CHK[k][1] for k in g.index], textfont=dict(color=INK),
                               hovertemplate="%{y}<br>%{x} " + T("hv_findings") + "<br><i>%{customdata}</i><extra></extra>"))
        chart(base_layout(fig, h=max(320, 24 * len(g) + 40)))

    with st.container(key="glass-log"):
        card_head(f":material/list_alt: {T('dq_log')}", T("dq_log_d"))
        f1, f2, f3, f4 = st.columns([2.3, 1, 1.3, 1.6])
        sev_sel = synced("pills", f1, T("severity"), SEVERITY_ORDER, "i_sev", selection_mode="multi",
                         default=SEVERITY_ORDER[:4], format_func=lambda s: f"{SEV_ICON[s]} {T.sev(s)}")
        dim_sel = synced("selectbox", f2, T("dimension"), [""] + DIMS, "i_dim",
                         format_func=lambda s: T.dim(s) if s else T("all"))
        sh_sel = f3.selectbox(T("sheet"), [""] + sorted(ISS["sheet"].dropna().unique()),
                              format_func=lambda s: s or T("all"), key="i_sheet")
        ck_sel = synced("selectbox", f4, T("check"), [""] + sorted(ISS["check_id"].unique(), key=lambda c: list(CHECKS).index(c)),
                        "i_check", format_func=lambda c: f"{c} · {CHK[c][0]}" if c else T("all"))
        g1, g2 = st.columns([1, 2])
        scope = synced("selectbox", g1, T("scope"), ["all", "counted", "primary"], "i_scope",
                       format_func=lambda s: T({"all": "sc_all", "counted": "sc_counted", "primary": "sc_primary"}[s]))
        iq = g2.text_input(T("search_detail"), key="i_q")
        I = ISS[ISS["severity"].isin(sev_sel or [])]
        if dim_sel:
            I = I[I["dimension"] == dim_sel]
        if sh_sel:
            I = I[I["sheet"] == sh_sel]
        if ck_sel:
            I = I[I["check_id"] == ck_sel]
        if scope == "counted":
            I = I[I["in_portfolio"] | I["uid"].isna()]
        elif scope == "primary":
            I = I[I["role"].isin(["primary"]) | I["role"].isna()]
        if iq:
            I = I[(I["message"] + " " + I["name"].fillna("") + " " + I["code"].fillna("")).str.lower()
                  .str.contains(iq.lower(), regex=False)]
        I = I.assign(_o=I["severity"].map(SEVERITY_ORDER.index)).sort_values(["_o", "check_id", "sheet", "row"])
        show = I[["severity", "check_id", "sheet", "row", "code", "name", "message"]].copy()
        show.insert(2, "title", I["check_id"].map(lambda c: CHK[c][0]))
        show["severity"] = show["severity"].map(sev_label)
        show[["code", "name"]] = show[["code", "name"]].fillna("–")
        ev = st.dataframe(show, hide_index=True, width="stretch", height=420, on_select="rerun",
                          selection_mode="single-row", key="issue_df",
                          column_config={"severity": T("severity"), "check_id": T("check"),
                                         "title": st.column_config.TextColumn(T("col_desc"), width="medium"),
                                         "sheet": T("col_sheet"), "row": st.column_config.NumberColumn(T("col_row"), format="%d"),
                                         "code": T("col_code"), "name": st.column_config.TextColumn(T("col_activity"), width="medium"),
                                         "message": st.column_config.TextColumn(T("col_detail"), width="large")})
        d1, d2 = st.columns([3, 1])
        d1.caption(T("shown", n=f"{len(I):,}"))
        d2.download_button(T("dl_issues"), to_csv(I, ISSUE_COLUMNS), "AOP2027_issues_filtered.csv", "text/csv",
                           width="stretch", icon=":material/download:")
        if ev.selection.rows:
            sel = I.iloc[ev.selection.rows[0]]
            st.info(f"**{sel['check_id']} – {CHK[sel['check_id']][0]}** · {T('about_check')}: {CHK[sel['check_id']][1]}",
                    icon=":material/info:")
            if pd.notna(sel["uid"]):
                line_details(DF[DF["uid"] == sel["uid"]].iloc[0])

    sec("✓", T("recon"), T("recon_d"))
    with st.container(key="glass-score"):
        card_head(f":material/scoreboard: {T('scorecard')}", T("scorecard_d"))
        sc = SHEETS[SHEETS["budget_lines"] > 0].copy()
        sc["difference"] = (sc["declared_total"].fillna(sc["lines_total"]) - sc["lines_total"]).round(2)
        sc["role"] = sc["role"].map(T.role)
        st.dataframe(sc[["short", "sheet", "role", "budget_lines", "declared_total", "lines_total", "difference",
                         "counted_total", "critical", "high", "medium", "low", "clean_line_pct"]],
                     hide_index=True, width="stretch",
                     column_config={"short": T("col_plan"), "sheet": T("col_sheet"), "role": T("col_role"),
                                    "budget_lines": T("col_lines"), "declared_total": money(T("col_sheet_total")),
                                    "lines_total": money(T("col_sum_lines")), "difference": money(T("col_diff")),
                                    "counted_total": money(T("col_counted")), "critical": T.sev("Critical"),
                                    "high": T.sev("High"), "medium": T.sev("Medium"), "low": T.sev("Low"),
                                    "clean_line_pct": st.column_config.ProgressColumn(T("col_clean"), format="%.0f%%",
                                                                                      min_value=0, max_value=100)})
    left, right = st.columns(2)
    with left, st.container(key="glass-summ"):
        card_head(f":material/compare_arrows: {T('summ')}")
        SR = pd.DataFrame(A["summary_recon"])
        SR["status"] = SR["status"].map(lambda x: "✓" if x == "match" else f"▲ {x}") + \
            SR["external_link"].map(lambda e: " · external link" if e else "")
        st.dataframe(SR[["summary_sheet", "summary_row", "component", "compared_with", "summary_total", "detail_total",
                         "difference", "status", "summary_q", "detail_q"]], hide_index=True, width="stretch",
                     column_config={"summary_sheet": T("col_sheet"), "summary_row": st.column_config.NumberColumn(T("col_row"), format="%d"),
                                    "component": T("col_item"), "compared_with": T("col_compared"),
                                    "summary_total": money(T("col_summary")), "detail_total": money(T("col_detail_v")),
                                    "difference": money(T("col_diff")), "status": T("col_status"),
                                    "summary_q": f"Q1–Q4 {T('col_summary')}", "detail_q": f"Q1–Q4 {T('col_detail_v')}"})
    with right, st.container(key="glass-vers"):
        card_head(f":material/difference: {T('vers')}", T("vers_d"))
        V = pd.DataFrame(A["versions"])
        p1, p2 = st.columns([2, 1])
        pair = p1.selectbox(T("comparison"), list(dict.fromkeys(V["pair"])), key="v_pair")
        only = p2.toggle(T("diff_only"), True, key="v_only")
        VV = V[V["pair"] == pair]
        if only:
            VV = VV[VV["status"] != "same"]
        st.dataframe(VV[["code", "name", "total_a", "total_b", "difference", "status", "q_a", "q_b"]], hide_index=True,
                     width="stretch",
                     column_config={"code": T("col_code"), "name": st.column_config.TextColumn(T("col_activity"), width="medium"),
                                    "total_a": money(VV["version_a"].iloc[0] if len(VV) else "A"),
                                    "total_b": money(VV["version_b"].iloc[0] if len(VV) else "B"),
                                    "difference": money("A − B"), "status": T("col_status"), "q_a": "Q1–Q4 A", "q_b": "Q1–Q4 B"})
        if not len(VV):
            st.success(T("no_diff"), icon=":material/check_circle:")

# =========================================================================== 3 OUTLIERS
with tabs[2]:
    sec(3, T("ol_title"), T("ol_desc"))
    uc_out = set(OUT[OUT["metric"] == "Unit cost (USD)"]["uid"]) if len(OUT) else set()
    U = L[L["unit_cost_usd"].fillna(0) > 0].copy()
    with st.container(key="glass-strip"):
        card_head(f":material/scatter_plot: {T('ol_strip')}", T("ol_strip_d"))
        if len(U):
            cats = U["activity_category"].value_counts().index.tolist()[::-1]
            U["lx"] = U["unit_cost_usd"].map(math.log10)
            U["yi"] = U["activity_category"].map(cats.index) + ((U.reset_index().index * 7919) % 13 - 6).values * 0.025
            U["out"] = U["uid"].isin(uc_out)
            fig = go.Figure()
            for cat in cats:
                stt = A["uc_stats"].get(cat)
                if stt:
                    y = cats.index(cat)
                    fig.add_shape(type="rect", x0=math.log10(stt["lower_fence"]), x1=math.log10(stt["upper_fence"]),
                                  y0=y - .32, y1=y + .32, fillcolor=BAND, line_width=0, layer="below")
                    fig.add_shape(type="line", x0=math.log10(stt["median"]), x1=math.log10(stt["median"]),
                                  y0=y - .38, y1=y + .38, line=dict(color=MEDIAN, width=2))
            for flag, color, name, sym, size, op in [(False, G1, T("within"), "circle", 8, .55),
                                                     (True, OUTLIER, T("outlier"), "diamond", 11, 1)]:
                d = U[U["out"] == flag]
                fig.add_trace(go.Scatter(x=d["lx"], y=d["yi"], mode="markers", name=name,
                                         marker=dict(color=color, size=size, opacity=op, symbol=sym, line=dict(width=1.5, color=RING)),
                                         customdata=d[["code", "name", "sheet_short", "excel_row", "unit_cost_usd"]].fillna("").values,
                                         hovertemplate="<b>%{customdata[0]} %{customdata[1]}</b><br>%{customdata[2]} · "
                                                       + T("col_row") + " %{customdata[3]}<br>" + T("hv_unit_cost")
                                                       + " $%{customdata[4]:,.2f}<extra>" + name + "</extra>"))
            tv, tt = log_ticks(U["lx"].min(), U["lx"].max())
            base_layout(fig, h=max(330, 35 * len(cats) + 60), showlegend=True,
                        legend=dict(orientation="h", y=1.05, x=1, xanchor="right"))
            fig.update_xaxes(tickvals=tv, ticktext=tt)
            fig.update_yaxes(tickvals=list(range(len(cats))),
                             ticktext=[f"{T.cat(c)} ({(U['activity_category'] == c).sum()})" for c in cats])
            chart(fig)
        else:
            st.caption(T("no_uc"))
    left, right = st.columns(2)
    with left, st.container(key="glass-hist"):
        card_head(f":material/equalizer: {T('ol_hist')}", T("ol_hist_d"))
        TT = L[L["budget_total"].fillna(0) > 0]["budget_total"]
        if len(TT):
            lx = TT.map(math.log10)
            lo, hi = math.floor(lx.min()), math.ceil(lx.max())
            edges = [lo + i * .25 for i in range(int((hi - lo) / .25) + 1)]
            cnt = pd.cut(lx, edges, include_lowest=True).value_counts(sort=False)
            mids = [(a + b) / 2 for a, b in zip(edges[:-1], edges[1:])]
            fig = go.Figure(go.Bar(x=mids, y=cnt.values, width=.22, marker=dict(color=G1, cornerradius=3),
                                   customdata=[[usd(10 ** a), usd(10 ** b)] for a, b in zip(edges[:-1], edges[1:])],
                                   hovertemplate="%{customdata[0]} – %{customdata[1]}<br>%{y} " + T("hv_lines") + "<extra></extra>"))
            ts = A["total_stats"]
            if ts:
                for v, name in [(ts["lower_fence"], T("lower_fence")), (ts["upper_fence"], T("upper_fence"))]:
                    fig.add_vline(x=math.log10(v), line=dict(color=OUTLIER, dash="dash", width=1.5),
                                  annotation_text=name, annotation_font=dict(size=11, family=FONT))
            tv, tt = log_ticks(lo, hi)
            base_layout(fig, h=300, bargap=0.1)
            fig.update_xaxes(tickvals=tv, ticktext=tt, showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor=GRID)
            chart(fig)
    with right, st.container(key="glass-bench"):
        card_head(f":material/straighten: {T('ol_bench')}", T("ol_bench_d"))
        B = pd.DataFrame([dict(category=T.cat(k), **v) for k, v in A["uc_stats"].items()]).sort_values("n", ascending=False)
        st.dataframe(B[["category", "n", "q1", "median", "q3", "upper_fence"]], hide_index=True, width="stretch",
                     column_config={"category": T("col_cat"), "n": T("col_lines"), "q1": money("P25"),
                                    "median": money("P50"), "q3": money("P75"), "upper_fence": money(T("upper_fence"))})
    with st.container(key="glass-flag"):
        card_head(f":material/flag: {T('ol_flag')}", T("ol_flag_d"))
        O = OUT[OUT["uid"].isin(set(L["uid"]))] if len(OUT) else OUT
        mt = synced("segmented_control", st, T("test"), ["All"] + list(dict.fromkeys(OUT["metric"])), "o_metric",
                    default="All", format_func=lambda m: T("all") if m == "All" else METRIC.get(m, m))
        if mt and mt != "All":
            O = O[O["metric"] == mt]
        OS = O[["metric", "sheet_short", "excel_row", "code", "name", "value", "peer_median", "robust_z", "direction",
                "peer_group"]].copy()
        OS["metric"] = OS["metric"].map(lambda m: METRIC.get(m, m))
        OS["peer_group"] = OS["peer_group"].map(T.cat)
        ev = st.dataframe(OS, hide_index=True, width="stretch", height=380, on_select="rerun", selection_mode="single-row",
                          key="out_df",
                          column_config={"metric": T("col_test"), "sheet_short": T("col_plan"),
                                         "excel_row": st.column_config.NumberColumn(T("col_row"), format="%d"),
                                         "code": T("col_code"), "name": st.column_config.TextColumn(T("col_activity"), width="large"),
                                         "value": money(T("col_value")), "peer_median": money(T("col_peer")),
                                         "robust_z": st.column_config.NumberColumn(T("col_z"), format="%.1f"),
                                         "direction": T("col_dir"), "peer_group": T("col_group")})
        st.download_button(T("dl_out"), to_csv(O), "AOP2027_outliers.csv", "text/csv", icon=":material/download:")
        if ev.selection.rows:
            line_details(DF[DF["uid"] == O.iloc[ev.selection.rows[0]]["uid"]].iloc[0])

# =========================================================================== 4 EXPLORE
with tabs[3]:
    sec(4, T("ex_title"), T("ex_desc"))
    left, right = st.columns(2)
    P = L[L["budget_total"].fillna(0) > 0].sort_values("budget_total", ascending=False)
    with left, st.container(key="glass-pareto"):
        tot = P["budget_total"].sum() or 1
        cum = P["budget_total"].cumsum() / tot * 100
        top10 = P["budget_total"].head(10).sum() / tot * 100
        card_head(f":material/show_chart: {T('ex_pareto')}", T("ex_pareto_d", p=f"{top10:.0f}", v=usd(tot)))
        fig = go.Figure(go.Scatter(x=list(range(1, len(P) + 1)), y=cum, mode="lines", line=dict(color=G1, width=2),
                                   fill="tozeroy", fillcolor=FILL,
                                   customdata=P[["code", "name", "budget_total"]].fillna("").values,
                                   hovertemplate="Top %{x}: %{y:.1f}%<br>#%{x} %{customdata[0]} %{customdata[1]} · $%{customdata[2]:,.0f}<extra></extra>"))
        if len(P):
            k80 = int((cum >= 80).values.argmax()) + 1
            fig.add_trace(go.Scatter(x=[k80], y=[cum.iloc[k80 - 1]], mode="markers+text", text=["  " + T("ex_80", k=k80)],
                                     textposition="middle right", textfont=dict(color=INK),
                                     marker=dict(color=G1, size=10, line=dict(color=RING, width=2)), hoverinfo="skip"))
        base_layout(fig, h=285, hovermode="x")
        fig.update_yaxes(range=[0, 102], ticksuffix="%", showgrid=True, gridcolor=GRID)
        fig.update_xaxes(title=T("ex_pareto_x"), showgrid=False)
        chart(fig)
    with right, st.container(key="glass-bands"):
        card_head(f":material/stacked_bar_chart: {T('ex_bands')}", T("ex_bands_d"))
        bands = [(0, 1e3, "< 1K"), (1e3, 1e4, "1–10K"), (1e4, 5e4, "10–50K"), (5e4, 1e5, "50–100K"),
                 (1e5, 5e5, "100–500K"), (5e5, 1e6, "0.5–1M"), (1e6, float("inf"), "> 1M")]
        bd = [(lab, P[(P["budget_total"] >= a) & (P["budget_total"] < b)]) for a, b, lab in bands]
        fig = go.Figure(go.Bar(x=[b[0] for b in bd], y=[len(b[1]) for b in bd], marker=dict(color=G1, cornerradius=5),
                               width=.42, text=[len(b[1]) for b in bd], textposition="outside", cliponaxis=False,
                               textfont=dict(color=INK), customdata=[usd(b[1]["budget_total"].sum(), True) for b in bd],
                               hovertemplate="%{x}: %{y} " + T("hv_lines") + " · %{customdata}<extra></extra>"))
        base_layout(fig, h=285)
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor=GRID)
        chart(fig)
    left, right = st.columns(2)
    with left, st.container(key="glass-catq"):
        card_head(f":material/view_module: {T('ex_catq')}", T("ex_catq_d"))
        g = L.groupby("activity_category")[[f"budget_q{i}" for i in range(1, 5)]].sum()
        g = g[g.sum(axis=1) > 0]
        g = g.loc[g.sum(axis=1).sort_values().index]
        sh = g.div(g.sum(axis=1), axis=0) * 100
        fig = go.Figure(go.Heatmap(z=sh.values, x=["Q1", "Q2", "Q3", "Q4"], y=[T.cat(c) for c in sh.index],
                                   text=sh.round(0).values, texttemplate="%{text:.0f}%",
                                   colorscale=[[i / 6, c] for i, c in enumerate(SEQ)], zmin=0, zmax=100, xgap=3, ygap=3,
                                   showscale=False, customdata=g.values,
                                   hovertemplate="<b>%{y}</b> · %{x}<br>%{z:.1f}% · $%{customdata:,.0f}<extra></extra>"))
        base_layout(fig, h=max(290, 25 * len(sh) + 40))
        fig.update_xaxes(showgrid=False, side="top")
        chart(fig)
    with right, st.container(key="glass-agency"):
        card_head(f":material/apartment: {T('ex_ag')}", T("ex_ag_d"))
        g = L.groupby("implementing_agency").agg(v=("budget_total", "sum"), n=("uid", "size")).sort_values("v").tail(15)
        chart(hbar([T.agency(a) for a in g.index], g["v"].tolist(), custom=g["n"].tolist(),
                   hover="<b>%{y}</b><br>%{x:$,.0f} · %{customdata} " + T("hv_lines") + "<extra></extra>"))
    with st.container(key="glass-pivot"):
        card_head(f":material/table_chart: {T('ex_pivot')}")
        dims = {"sheet_label": T("g_plan"), "activity_category": T("g_cat"), "implementing_agency": T("g_ag"),
                "implementation_level": T("g_level"), "modality": T("g_mod"), "component": T("g_comp"), "unit": T("g_unit")}
        dim = synced("selectbox", st, T("group_by"), list(dims), "pivot_dim", format_func=dims.get)
        src = L.assign(**{dim: L[dim].fillna("(blank)")})
        if dim == "sheet_label":
            src["sheet_label"] = src["sheet"].map(LABEL)
        pv = (src.groupby(dim).agg(lines=("uid", "size"), q1=("budget_q1", "sum"), q2=("budget_q2", "sum"),
                                   q3=("budget_q3", "sum"), q4=("budget_q4", "sum"), total=("budget_total", "sum"),
                                   with_issues=("material", "sum"))
              .sort_values("total", ascending=False).reset_index())
        tr = {"activity_category": T.cat, "implementing_agency": T.agency, "implementation_level": T.level,
              "component": T.comp}.get(dim)
        if tr:
            pv[dim] = pv[dim].map(tr)
        pv["share_pct"] = pv["total"] / max(1, pv["total"].sum()) * 100
        st.dataframe(pv, hide_index=True, width="stretch",
                     column_config={**{c: money(c.upper()) for c in ["q1", "q2", "q3", "q4"]}, "total": money(T("col_total")),
                                    dim: dims[dim], "lines": T("col_lines"), "with_issues": T("col_mat"),
                                    "share_pct": st.column_config.ProgressColumn(T("col_share"), format="%.1f%%",
                                                                                 min_value=0, max_value=100)})
        st.download_button(T("dl_pivot"), to_csv(pv), f"AOP2027_breakdown_{dim}.csv", "text/csv", icon=":material/download:")

# =========================================================================== 5 TABLE
with tabs[4]:
    sec(5, T("tb_title"), T("tb_desc"))
    with st.container(key="glass-table"):
        scope = synced("segmented_control", st, T("rows"), ["counted", "all", "excluded"], "t_scope", default="counted",
                       format_func=lambda s: T({"counted": "r_counted", "all": "r_all", "excluded": "r_excl"}[s]))
        base = {"all": DF, "excluded": DF[~DF["in_portfolio"]]}.get(scope, COUNTED)
        TB = apply_filters(base).sort_values("budget_total", ascending=False, na_position="last")
        st.caption(T("tb_count", n=f"{len(TB):,}", v=usd(TB[TB["in_portfolio"]]["budget_total"].sum(), True)))
        cols = ["sheet", "excel_row", "code", "name", "activity_category", "unit_cost_usd", "quantity",
                "budget_q1", "budget_q2", "budget_q3", "budget_q4", "budget_total", "implementing_agency",
                "max_severity", "issue_count"]
        if scope not in (None, "counted"):
            cols += ["row_kind", "exclusion_reason"]
        selectable_lines(TB, "line_df", cols, height=560)
        st.download_button(T("dl_rows"), to_csv(TB, LINE_COLUMNS), "AOP2027_rows_filtered.csv", "text/csv",
                           type="primary", icon=":material/download:")

# =========================================================================== 6 STRUCTURE
with tabs[5]:
    layouts = sorted({l["layout"] for l in A["layouts"]})
    sec(6, T("st_title"), T("st_desc", f=M["source"], s=M["sheets_total"], h=len(M["hidden"]), l=len(layouts),
                            p=M["parsed_rows"], c=M["counted_lines"]))
    with st.container(key="glass-inv"):
        card_head(f":material/inventory_2: {T('st_inv')}")
        INV = SHEETS.copy()
        INV["label"] = INV["sheet"].map(LABEL).fillna(INV["label"])
        INV["role"] = INV["role"].map(T.role)
        st.dataframe(INV[["sheet", "label", "role", "visibility", "layout", "used_range", "merged_ranges", "formulas",
                          "parsed_rows", "budget_lines", "subtotal_rows", "counted_lines", "counted_total"]],
                     hide_index=True, width="stretch", height=430,
                     column_config={"sheet": T("col_sheet"), "label": st.column_config.TextColumn(T("col_content"), width="medium"),
                                    "role": T("col_role"), "visibility": T("col_visible"), "layout": T("col_layout"),
                                    "used_range": T("col_used"), "formulas": T("col_formulas"), "parsed_rows": T("col_parsed"),
                                    "budget_lines": T("col_lines"), "subtotal_rows": T("col_sub"), "counted_lines": T("col_counted"),
                                    "counted_total": money(T("col_counted_usd"))})
    left, right = st.columns(2)
    PR = pd.DataFrame(A["profile"])
    with left, st.container(key="glass-schema"):
        card_head(f":material/schema: {T('st_schema')}")
        st.dataframe(PR[["field", "type", "description", "completeness_pct", "missing", "unique", "top_values"]],
                     hide_index=True, width="stretch", height=520,
                     column_config={"field": T("col_field"), "type": T("col_type"),
                                    "description": st.column_config.TextColumn(T("col_desc"), width="medium"),
                                    "completeness_pct": st.column_config.ProgressColumn(T("col_complete"), format="%.0f%%",
                                                                                        min_value=0, max_value=100),
                                    "missing": T("col_missing"), "unique": T("col_unique"), "top_values": T("col_top")})
    with right, st.container(key="glass-stats"):
        card_head(f":material/functions: {T('st_stats')}")
        nums = PR[PR["type"] == "number"][["field", "non_missing", "min", "p25", "median", "mean", "p75", "max", "std", "sum"]]
        st.dataframe(nums, hide_index=True, width="stretch",
                     column_config={"field": T("col_field"), **{c: st.column_config.NumberColumn(format="localized")
                                                              for c in ["min", "p25", "median", "mean", "p75", "max", "std", "sum"]}})
        card_head(f":material/currency_exchange: {T('st_fx')}")
        st.dataframe(pd.DataFrame(A["fx"]), hide_index=True, width="stretch")
        with st.expander(T("st_links", n=len(A["external_links"])), icon=":material/link:"):
            st.dataframe(pd.DataFrame({"target": A["external_links"]}), hide_index=True, width="stretch")
    with st.container(key="glass-map"):
        card_head(f":material/view_column: {T('st_map')}")
        st.dataframe(pd.DataFrame(A["layouts"]), hide_index=True, width="stretch")
    with st.container(key="glass-cat-list"):
        card_head(f":material/rule: {T('st_cat')}")
        st.dataframe(pd.DataFrame([dict(check=k, dimension=T.dim(d), title=CHK[k][0], severity=T.sev(s),
                                         explanation=CHK[k][1], findings=int((ISS["check_id"] == k).sum()))
                                   for k, (d, t, s, e) in CHECKS.items()]),
                     hide_index=True, width="stretch",
                     column_config={"check": T("check"), "dimension": T("dimension"), "title": T("col_title"),
                                    "severity": T("severity"), "findings": T("col_findings"),
                                    "explanation": st.column_config.TextColumn(T("col_expl"), width="large")})

# =========================================================================== 7 EXPORT
with tabs[6]:
    sec(7, T("xp_title"), T("xp_desc"))
    F = A["files"]
    XL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    items = [
        ("table_view", T("xp_clean"), T("xp_clean_d"),
         [(T("b_excel"), F["cleaned_xlsx"], "AOP2027_cleaned_dataset.xlsx", XL),
          (T("b_counted"), to_csv(COUNTED, LINE_COLUMNS), "AOP2027_counted_lines.csv", "text/csv"),
          (T("b_filtered"), to_csv(L, LINE_COLUMNS), "AOP2027_lines_filtered.csv", "text/csv")]),
        ("fact_check", T("xp_q"), T("xp_q_d", n=len(ISS)),
         [(T("b_excel"), F["quality_xlsx"], "AOP2027_data_quality_report.xlsx", XL),
          (T("b_issues"), to_csv(ISS, ISSUE_COLUMNS), "AOP2027_issues.csv", "text/csv")]),
        ("analytics", T("xp_a"), T("xp_a_d"),
         [(T("b_excel"), F["analysis_xlsx"], "AOP2027_analysis_results.xlsx", XL),
          (T("dl_out"), to_csv(OUT), "AOP2027_outliers.csv", "text/csv")]),
        ("dataset", T("xp_rows"), T("xp_rows_d"),
         [("CSV", to_csv(DF, LINE_COLUMNS), "AOP2027_all_parsed_rows.csv", "text/csv")]),
        ("web", T("xp_html"), T("xp_html_d"),
         [("HTML", F["dashboard"], "AOP2027_dashboard.html", "text/html")]),
        ("data_object", T("xp_json"), T("xp_json_d"),
         [("JSON", json.dumps({k: v for k, v in A.items() if k != "files"}, default=str, ensure_ascii=False).encode("utf-8"),
           "AOP2027_analysis.json", "application/json")]),
    ]
    for row in (items[:3], items[3:]):
        cols = st.columns(3)
        for c, (icon, title, desc, btns) in zip(cols, row):
            with c, st.container(key=f"glass-x-{icon}"):
                card_head(f":material/{icon}: {title}", desc)
                for i, (lab, data, fn, mime) in enumerate(btns):
                    st.download_button(lab, data, fn, mime, key=f"dl_{fn}", width="stretch", icon=":material/download:",
                                       type="primary" if i == 0 else "secondary")
