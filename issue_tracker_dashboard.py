import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="NOC Insights Compass",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: #080c14;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1923 0%, #080c14 100%);
        border-right: 1px solid rgba(59, 130, 246, 0.2);
    }
    
    /* Glassmorphism KPI Cards */
    .kpi-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(59, 130, 246, 0.15);
        border-radius: 16px;
        padding: 12px 10px;
        text-align: center;
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.6s ease forwards;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        opacity: 0;
        transition: opacity 0.3s;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        border-color: rgba(59, 130, 246, 0.4);
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.15);
    }
    .kpi-card:hover::before { opacity: 1; }
    
    /* Animated number pulse */
    @keyframes countPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .kpi-card:hover .kpi-value {
        animation: countPulse 0.5s ease;
    }
    
    /* Sparkline glow on hover */
    .kpi-card:hover svg polyline {
        filter: drop-shadow(0 0 6px currentColor);
    }
    
    /* Staggered card animations */
    .kpi-card-1 { animation-delay: 0s; }
    .kpi-card-2 { animation-delay: 0.15s; }
    .kpi-card-3 { animation-delay: 0.3s; }
    .kpi-card-4 { animation-delay: 0.45s; }
    
    /* Visual KPI cards must never intercept clicks meant for the button below */
    .kpi-card { cursor: default; pointer-events: none; }
    .kpi-value {
        font-size: 1.2rem;
        font-weight: 700;
        margin: 3px 0;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .kpi-label {
        font-size: 0.6rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    .kpi-icon {
        font-size: 1rem;
        margin-bottom: 2px;
        opacity: 0.8;
    }
    
    /* Gradient Header */
    .main-header {
        text-align: center;
        padding: 20px 0;
        margin-bottom: 20px;
    }
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #60a5fa, #a78bfa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .main-header p {
        color: #94a3b8;
        font-size: 1rem;
        margin-top: 5px;
    }
    
    /* Section headers with gradient underline */
    .section-header {
        color: #e2e8f0;
        border-bottom: 2px solid transparent;
        border-image: linear-gradient(90deg, #60a5fa, #a78bfa) 1;
        padding-bottom: 8px;
        margin: 30px 0 15px 0;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(59, 130, 246, 0.15);
        border-radius: 12px;
        padding: 15px;
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: rgba(59, 130, 246, 0.4);
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.1);
    }
    [data-testid="stMetricValue"] {
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    hr {
        border-color: rgba(59, 130, 246, 0.15);
    }
    
    /* KPI Buttons */
    .stButton > button {
        width: 100%;
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(59, 130, 246, 0.15) !important;
        border-radius: 12px !important;
        padding: 15px 25px !important;
        color: #e2e8f0 !important;
        transition: all 0.3s ease !important;
        min-height: auto !important;
        height: 70px !important;
        font-size: 0.9rem !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        line-height: 1.4 !important;
        backdrop-filter: blur(20px) !important;
    }
    .stButton > button:hover {
        border-color: rgba(59, 130, 246, 0.5) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.2) !important;
        color: #60a5fa !important;
    }
    .stButton > button:active, .stButton > button:focus {
        border-color: rgba(139, 92, 246, 0.5) !important;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.3) !important;
    }
    
    /* Override for toggle buttons in header */
    [data-testid="stColumn"] [data-testid="stColumn"] .stButton > button {
        height: auto !important;
        min-height: auto !important;
        padding: 8px 10px !important;
        font-size: 0.75rem !important;
        border-radius: 8px !important;
    }

    /* ===== KPI unified card: border/bg on the container, children blend in ===== */
    .st-key-kpicard_total_issues,
    .st-key-kpicard_downtime,
    .st-key-kpicard_opco,
    .st-key-kpicard_top_cat {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(59, 130, 246, 0.15);
        border-radius: 16px;
        padding: 6px 6px 4px;
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
        overflow: hidden;
    }
    .st-key-kpicard_total_issues:hover,
    .st-key-kpicard_downtime:hover,
    .st-key-kpicard_opco:hover,
    .st-key-kpicard_top_cat:hover {
        transform: translateY(-4px);
        border-color: rgba(59, 130, 246, 0.4);
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.15);
    }
    /* Kill the vertical gap between the button and the sparkline inside the card */
    .st-key-kpicard_total_issues [data-testid="stVerticalBlock"],
    .st-key-kpicard_downtime [data-testid="stVerticalBlock"],
    .st-key-kpicard_opco [data-testid="stVerticalBlock"],
    .st-key-kpicard_top_cat [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
    /* Button inside a KPI card: transparent, borderless, no own card look */
    .st-key-kpicard_total_issues .stButton > button,
    .st-key-kpicard_downtime .stButton > button,
    .st-key-kpicard_opco .stButton > button,
    .st-key-kpicard_top_cat .stButton > button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        height: auto !important;
        min-height: 90px !important;
        white-space: normal !important;
        padding: 10px 8px 0 !important;
        transform: none !important;
    }
    .st-key-kpicard_total_issues .stButton > button:hover,
    .st-key-kpicard_downtime .stButton > button:hover,
    .st-key-kpicard_opco .stButton > button:hover,
    .st-key-kpicard_top_cat .stButton > button:hover {
        transform: none !important;
        box-shadow: none !important;
        color: #60a5fa !important;
    }
    /* Sparkline: no own border/bg, just the SVG under the button */
    .kpi-spark {
        padding: 0 6px 4px;
        text-align: center;
    }
    .kpi-spark svg {
        margin: 0 auto !important;
        display: block;
        max-width: 100% !important;
    }
    
    /* Disable search/typing in selectbox */
    [data-baseweb="select"] input {
        pointer-events: none !important;
        caret-color: transparent !important;
    }
    
    /* Reduce top space */
    .block-container {
        padding-top: 1rem !important;
    }
    [data-testid="stHeader"] {
        height: 2rem !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(59, 130, 246, 0.15) !important;
        border-radius: 10px !important;
    }
    
    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(59, 130, 246, 0.1);
    }
    
    /* Category cards */
    .cat-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(59, 130, 246, 0.15);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .cat-card:hover {
        transform: translateY(-4px);
        border-color: rgba(59, 130, 246, 0.4);
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.15);
    }
    .cat-card .cat-icon { font-size: 1.8rem; margin-bottom: 8px; }
    .cat-card .cat-value { font-size: 1.8rem; font-weight: 700; margin-bottom: 4px; }
    .cat-card .cat-name { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Viewing badge */
    .viewing-badge {
        text-align: center;
        margin-bottom: 15px;
    }
    .viewing-badge span {
        padding: 5px 20px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        backdrop-filter: blur(10px);
    }

    /* Animated counter keyframes */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-in {
        animation: fadeInUp 0.6s ease forwards;
    }
</style>
""", unsafe_allow_html=True)

# Customer configurations
CUSTOMERS = {
    "🔵 Airtel Africa / OBF": {
        "file": "Issue Tracker AA_OBF.xlsx",
        "color": "#00d4ff",
        "accent": "#1e3a5f"
    },
    "🟡 MTN": {
        "file": "Issue Tracker  MTN.xlsx",
        "color": "#ffc107",
        "accent": "#5f4b1e"
    }
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@st.cache_data(ttl=300)
def load_all_sheets(file_path):
    xlsx = pd.ExcelFile(file_path)
    sheets = {}
    for name in xlsx.sheet_names:
        df = pd.read_excel(xlsx, sheet_name=name)
        sheets[name] = make_arrow_safe(df)
    return sheets


def make_arrow_safe(df):
    """Ensure a DataFrame can be serialized to an Arrow table for st.dataframe.

    Streamlit converts DataFrames to Arrow for display. Object columns that mix
    types (e.g. some cells str, some datetime) raise ArrowTypeError and the table
    fails to render. Casting such columns to string makes them display-safe.
    """
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == "object":
            # Check for mixed / non-string python objects in the column
            non_null = df[col].dropna()
            if not non_null.empty:
                types = set(type(v) for v in non_null)
                if len(types) > 1 or not all(t is str for t in types):
                    df[col] = df[col].apply(lambda v: "" if pd.isna(v) else str(v))
    return df


# Category colors & icons
CATEGORY_COLORS = {
    "MSDP Issue": "#3b82f6",
    "Autocaller Issue": "#f59e0b",
    "Test Alerts Issue": "#ef4444",
    "Auto TT Issue": "#10b981",
    "ITSM Issue": "#8b5cf6",
    "OneFM Issue ": "#06b6d4",
    "EtigerNG Issue ": "#ec4899"
}
CATEGORY_ICONS = {
    "MSDP Issue": "🔴",
    "Autocaller Issue": "📞",
    "Test Alerts Issue": "⚠️",
    "Auto TT Issue": "🎫",
    "ITSM Issue": "🔧",
    "OneFM Issue ": "📡",
    "EtigerNG Issue ": "🖥️"
}

# Session state
if "active_view" not in st.session_state:
    st.session_state.active_view = "home"
if "selected_customer" not in st.session_state:
    st.session_state.selected_customer = "🔵 Airtel Africa / OBF"

# ===== HEADER WITH CUSTOMER BUTTONS + MONTH FILTER =====
header_col1, header_col2, header_col3 = st.columns([1.5, 3, 1.5])

with header_col2:
    st.markdown("""
    <div style="text-align: center; padding-top: 5px;">
        <h1 style="font-size: 2rem; font-weight: 700; margin: 0;"><span style="font-size: 2rem;">🧭</span> <span style="background: linear-gradient(90deg, #60a5fa, #a78bfa, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">NOC Insights Compass</span></h1>
    </div>
    """, unsafe_allow_html=True)

with header_col3:
    st.markdown("<p style='font-size:0.7rem; color:#a0a0c0; margin:0; padding-top:15px; text-align:center;'>Switch Customer</p>", unsafe_allow_html=True)
    tcol1, tcol2 = st.columns(2)
    with tcol1:
        if st.button("🔵 AA/OBF", key="btn_aa", use_container_width=True):
            st.session_state.selected_customer = "🔵 Airtel Africa / OBF"
            st.session_state.active_view = "home"
            st.rerun()
    with tcol2:
        if st.button("🟡 MTN", key="btn_mtn", use_container_width=True):
            st.session_state.selected_customer = "🟡 MTN"
            st.session_state.active_view = "home"
            st.rerun()

selected_customer = st.session_state.selected_customer

# Load data for selected customer
customer_config = CUSTOMERS[selected_customer]
excel_path = os.path.join(BASE_DIR, customer_config["file"])

if not os.path.exists(excel_path):
    st.error(f"File not found: {customer_config['file']}")
    st.stop()

sheets_raw = load_all_sheets(excel_path)
customer_color = customer_config["color"]

# --- Month & Year Filter (next to customer buttons) ---
all_dates = set()
for df in sheets_raw.values():
    if "Date" in df.columns:
        dates = pd.to_datetime(df["Date"], errors="coerce").dropna()
        for d in dates:
            all_dates.add((d.year, d.month))

all_years = sorted(set(y for y, m in all_dates), reverse=True)
month_names = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

with header_col1:
    yr_col, mn_col = st.columns(2)
    with yr_col:
        selected_year = st.selectbox(
            "📅 Year",
            options=["All Years"] + [str(y) for y in all_years],
            index=0,
            key="year_filter"
        )
    with mn_col:
        if selected_year == "All Years":
            month_options = ["All Months"]
        else:
            available_months = sorted([m for y, m in all_dates if y == int(selected_year)])
            month_options = ["All Months"] + [month_names[m - 1] for m in available_months]
        selected_month_name = st.selectbox(
            "📅 Month",
            options=month_options,
            index=0,
            key="month_filter"
        )

# Filter sheets by selected year and month
if selected_year == "All Years":
    sheets = sheets_raw
else:
    filter_year = int(selected_year)
    filter_month = month_names.index(selected_month_name) + 1 if selected_month_name != "All Months" else None
    sheets = {}
    for name, df in sheets_raw.items():
        if "Date" in df.columns:
            df_copy = df.copy()
            df_copy["_parsed_date"] = pd.to_datetime(df_copy["Date"], errors="coerce")
            mask = df_copy["_parsed_date"].dt.year == filter_year
            if filter_month:
                mask = mask & (df_copy["_parsed_date"].dt.month == filter_month)
            filtered = df_copy[mask].drop(columns=["_parsed_date"])
            sheets[name] = filtered
        else:
            sheets[name] = df

# Show which customer is selected
st.markdown(f"""
<div class="viewing-badge">
    <span style="background: {customer_color}15; border: 1px solid {customer_color}44; color: {customer_color};">
        ● Viewing: {selected_customer}
    </span>
</div>
""", unsafe_allow_html=True)

# Compute global stats
total_issues = sum(len(df) for df in sheets.values())
non_empty_sheets = {k: v for k, v in sheets.items() if len(v) > 0}
top_category = max(sheets.items(), key=lambda x: len(x[1])) if sheets else ("N/A", pd.DataFrame())

# Parse duration strings into total minutes
import re
def parse_duration_to_minutes(val):
    """Parse various duration formats to total minutes."""
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return 0
        s = str(val).strip().lower()
        if not s or s == 'nan' or s == 'nat':
            return 0
        total = 0
        # Format: "00 HH : 30 MM" or "25 HH : 40 MM"
        hh_mm = re.search(r'(\d+)\s*hh\s*:\s*(\d+)\s*mm', s)
        if hh_mm:
            return int(hh_mm.group(1)) * 60 + int(hh_mm.group(2))
        # Format: "3 hours 30 minutes" / "1 hour 26 minutes"
        hours = re.search(r'(\d+)\s*hours?', s)
        mins = re.search(r'(\d+)\s*min(?:utes?|s)?', s)
        if hours:
            total += int(hours.group(1)) * 60
        if mins:
            total += int(mins.group(1))
        # Format: "1hrs 30 mins"
        hrs = re.search(r'(\d+)\s*hrs?', s)
        if hrs and not hours:
            total += int(hrs.group(1)) * 60
        return total
    except Exception:
        return 0

total_minutes = 0
for df in sheets.values():
    dur_col = [c for c in df.columns if 'duration' in c.lower()]
    if dur_col and len(df) > 0:
        mins = df[dur_col[0]].apply(parse_duration_to_minutes)
        total_minutes += int(mins.sum())

total_hours = int(total_minutes // 60)
remaining_mins = int(total_minutes % 60)
total_days = total_hours // 24
remaining_hours = total_hours % 24
total_months = total_days // 30
remaining_days = total_days % 30

if total_months > 0:
    total_downtime_str = f"{total_months}mo {remaining_days}d {remaining_hours}h"
elif total_days > 0:
    total_downtime_str = f"{total_days}d {remaining_hours}h {remaining_mins}m"
elif total_hours > 0:
    total_downtime_str = f"{total_hours}h {remaining_mins}m"
else:
    total_downtime_str = f"{remaining_mins}m"

# OPCO normalization mappings
OPCO_ALIASES = {
    "Africa": "South Africa",
}

# Region to individual OPCOs mapping
REGION_MAPPING = {
    "airtel east": ["Malawi", "Madagascar", "Zambia"],
    "airtel-west": ["Niger", "Gabon"],
    "airtel west": ["Niger", "Gabon"],
    "ndc": ["Tchad", "DRC", "Nigeria"],
}

# OPCOs to expand to all individual OPCOs (any entry containing these patterns)
OPCO_EXPAND_ALL = {"ALL MTN"}
OPCO_EXPAND_ALL_PATTERNS = ["all airtel", "all africa", "all opco"]


def get_all_individual_opcos(sheets_data):
    """Get all individual OPCOs (excluding group names)."""
    opcos = set()
    for df in sheets_data.values():
        opco_col = [c for c in df.columns if "opco" in c.lower()]
        if opco_col:
            for val in df[opco_col[0]].dropna().str.strip().unique():
                for o in str(val).split(","):
                    o = o.strip()
                    if not o:
                        continue
                    # Skip group entries
                    if o in OPCO_EXPAND_ALL:
                        continue
                    if any(p in o.lower() for p in OPCO_EXPAND_ALL_PATTERNS):
                        continue
                    # Check if it's a region name
                    if o.lower() in REGION_MAPPING:
                        opcos.update(REGION_MAPPING[o.lower()])
                        continue
                    o = OPCO_ALIASES.get(o, o)
                    opcos.add(o)
    return opcos


def normalize_opcos(raw_value, all_individual_opcos):
    """Split and normalize a raw OPCO value into individual OPCOs."""
    result = []
    for o in str(raw_value).split(","):
        o = o.strip()
        if not o or o == "nan":
            continue
        # Check if it's an "ALL" type entry
        if o in OPCO_EXPAND_ALL or any(p in o.lower() for p in OPCO_EXPAND_ALL_PATTERNS):
            result.extend(all_individual_opcos)
        # Check if it's a region name
        elif o.lower() in REGION_MAPPING:
            result.extend(REGION_MAPPING[o.lower()])
        else:
            o = OPCO_ALIASES.get(o, o)
            result.append(o)
    return result


# Get all individual OPCOs for expansion
all_individual_opcos = get_all_individual_opcos(sheets)

all_opcos = set()
opco_issue_counts_global = {}
for name, df in sheets.items():
    opco_col = [c for c in df.columns if "opco" in c.lower()]
    if opco_col:
        for val in df[opco_col[0]].dropna().str.strip().unique():
            all_opcos.update(normalize_opcos(val, all_individual_opcos))
        for _, row in df.iterrows():
            raw_opco = str(row[opco_col[0]]).strip()
            if raw_opco and raw_opco != "nan":
                for opco in normalize_opcos(raw_opco, all_individual_opcos):
                    opco_issue_counts_global[opco] = opco_issue_counts_global.get(opco, 0) + 1

most_affected_opco = max(opco_issue_counts_global, key=opco_issue_counts_global.get) if opco_issue_counts_global else "N/A"
most_affected_opco_count = opco_issue_counts_global.get(most_affected_opco, 0)

# Sidebar
with st.sidebar:
    st.markdown(f"## 🧭 {selected_customer}")
    st.markdown("---")
    
    if st.button("🏠 Home Dashboard", use_container_width=True):
        st.session_state.active_view = "home"
    
    st.markdown("**Quick Links:**")
    if st.button("📊 Total Issues View", use_container_width=True):
        st.session_state.active_view = "total_issues"
    if st.button("📂 Categories View", use_container_width=True):
        st.session_state.active_view = "categories"
    if top_category[0] != "N/A":
        if st.button(f"🔥 Top: {top_category[0].strip()}", use_container_width=True):
            st.session_state.active_view = "top_category"
    if st.button("🌍 OPCOs View", use_container_width=True):
        st.session_state.active_view = "opcos"
    
    st.markdown("---")
    st.markdown("**Individual Categories:**")
    for name in sheets.keys():
        icon = CATEGORY_ICONS.get(name, "📄")
        if st.button(f"{icon} {name.strip()}", key=f"side_{name}", use_container_width=True):
            st.session_state.active_view = f"sheet_{name}"
    
    st.markdown("---")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%d %b %Y, %H:%M')}")
    st.markdown(f"**Total Issues:** {total_issues}")


# ========== HOME VIEW ==========
if st.session_state.active_view == "home":
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <p style="color: #94a3b8;">Click any card below to drill down into details</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate sparkline data (last 12 months of issues)
    def get_monthly_counts(sheets_data):
        all_dates = []
        for df in sheets_data.values():
            if "Date" in df.columns:
                dates = pd.to_datetime(df["Date"], errors="coerce").dropna()
                all_dates.extend(dates.tolist())
        if not all_dates:
            return [0] * 12
        s = pd.Series(all_dates)
        monthly = s.dt.to_period("M").value_counts().sort_index()
        return monthly.tail(12).tolist() or [0] * 12
    
    def make_sparkline_svg(values, color="#60a5fa", width=120, height=35):
        if not values or max(values) == 0:
            return ""
        max_val = max(values)
        points = []
        for i, v in enumerate(values):
            x = (i / max(len(values) - 1, 1)) * width
            y = height - (v / max_val) * (height - 4) - 2
            points.append(f"{x:.1f},{y:.1f}")
        polyline = " ".join(points)
        # Fill area
        fill_points = f"0,{height} " + polyline + f" {width},{height}"
        gid = f"sparkGrad_{color.lstrip('#')}"
        return f'''<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" preserveAspectRatio="xMidYMid meet" style="display:block; margin:6px auto 0;">
            <defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="{color}" stop-opacity="0.3"/>
                <stop offset="100%" stop-color="{color}" stop-opacity="0.02"/>
            </linearGradient></defs>
            <polygon points="{fill_points}" fill="url(#{gid})"/>
            <polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>'''
    
    spark_data = get_monthly_counts(sheets_raw)

    def mini_spark(values, color, key):
        """Tiny native area chart used as a sparkline (renders reliably, unlike inline SVG)."""
        import plotly.graph_objects as _go
        vals = values if values and max(values) > 0 else [0, 0]
        h = color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        fill = f"rgba({r},{g},{b},0.15)"
        fig = _go.Figure(_go.Scatter(
            y=vals, mode="lines", line=dict(color=color, width=2, shape="spline"),
            fill="tozeroy", fillcolor=fill
        ))
        fig.update_layout(
            height=48, margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=key)

    # KPI Cards with sparklines
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        with st.container(key="kpicard_total_issues"):
            if st.button(f"📊\n\n**Total Issues**\n\n**{total_issues}**", key="kpi_total_issues", use_container_width=True):
                st.session_state.active_view = "total_issues"
                st.rerun()
            mini_spark(spark_data, "#60a5fa", "spark_total")
    
    with col2:
        with st.container(key="kpicard_downtime"):
            if st.button(f"⏱️\n\n**Total Downtime**\n\n**{total_downtime_str}**", key="kpi_downtime", use_container_width=True):
                st.session_state.active_view = "total_downtime"
                st.rerun()
            mini_spark(spark_data, "#a78bfa", "spark_downtime")
    
    with col3:
        with st.container(key="kpicard_opco"):
            if st.button(f"🌍\n\n**Most Affected OPCO**\n\n**{most_affected_opco}**\n\n{most_affected_opco_count} issues", key="kpi_opco", use_container_width=True):
                st.session_state.active_view = "opcos"
                st.rerun()
            mini_spark(spark_data, "#34d399", "spark_opco")
    
    with col4:
        top_cat_name = top_category[0].strip() if top_category[0] != "N/A" else "N/A"
        with st.container(key="kpicard_top_cat"):
            if st.button(f"🔥\n\n**Top Category**\n\n**{top_cat_name}**\n\n{len(top_category[1])} issues", key="kpi_top_cat", use_container_width=True):
                if top_category[0] != "N/A":
                    st.session_state.active_view = "top_category"
                    st.rerun()
            mini_spark(spark_data, "#f59e0b", "spark_topcat")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="section-header">📊 Issues by Category</div>', unsafe_allow_html=True)
        chart_data = pd.DataFrame({
            "Category": [k.strip() for k in sheets.keys()],
            "Count": [len(v) for v in sheets.values()]
        }).sort_values("Count", ascending=True)
        
        fig = px.bar(chart_data, x="Count", y="Category", orientation="h",
                     color="Count", color_continuous_scale=["#1e293b", "#60a5fa"], text="Count")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"), showlegend=False, coloraxis_showscale=False,
            margin=dict(l=0, r=20, t=10, b=0), height=300,
            xaxis=dict(showgrid=True, gridcolor="rgba(59,130,246,0.1)"), yaxis=dict(showgrid=False)
        )
        fig.update_traces(textposition="outside", textfont=dict(color="#60a5fa"))
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.markdown('<div class="section-header">🍩 Distribution</div>', unsafe_allow_html=True)
        pie_data = pd.DataFrame({
            "Category": [k.strip() for k in sheets.keys() if len(sheets[k]) > 0],
            "Count": [len(v) for v in sheets.values() if len(v) > 0]
        })
        if not pie_data.empty:
            fig_pie = px.pie(pie_data, values="Count", names="Category",
                             color_discrete_sequence=list(CATEGORY_COLORS.values()), hole=0.4)
            fig_pie.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"), margin=dict(l=0, r=0, t=10, b=0),
                height=300, legend=dict(font=dict(size=10))
            )
            fig_pie.update_traces(textinfo="percent+value", textfont=dict(color="white"))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No issues recorded yet.")
    
    # Category cards (clickable)
    st.markdown('<div class="section-header">📋 Click a Category to Explore</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (name, df) in enumerate(sheets.items()):
        with cols[i % 4]:
            icon = CATEGORY_ICONS.get(name, "📄")
            if st.button(f"{icon}\n\n**{len(df)}**\n\n{name.strip()}", key=f"card_{name}", use_container_width=True):
                st.session_state.active_view = f"sheet_{name}"
                st.rerun()


# ========== TOTAL ISSUES VIEW ==========
elif st.session_state.active_view == "total_issues":
    st.markdown(f"""
    <div class="main-header">
        <h1>📊 All Issues Overview</h1>
        <p>Complete view of all {total_issues} issues across all categories</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("← Back to Home"):
        st.session_state.active_view = "home"
        st.rerun()
    
    st.markdown("---")
    
    # ---- Top-line KPIs (always render) ----
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Issues", f"{total_issues:,}")
    m2.metric("Active Categories", len(non_empty_sheets))
    m3.metric("OPCOs Affected", len(all_opcos))
    m4.metric("Total Downtime", total_downtime_str)
    
    st.markdown("---")
    
    # ---- Issues by Category chart (always render) ----
    st.markdown('<div class="section-header">📊 Issues by Category</div>', unsafe_allow_html=True)
    cat_chart = pd.DataFrame({
        "Category": [k.strip() for k in sheets.keys()],
        "Count": [len(v) for v in sheets.values()]
    }).sort_values("Count", ascending=True)
    fig_cat = px.bar(cat_chart, x="Count", y="Category", orientation="h",
                     color="Count", color_continuous_scale=["#1e293b", customer_color], text="Count")
    fig_cat.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"), showlegend=False, coloraxis_showscale=False,
        margin=dict(l=0, r=20, t=10, b=0), height=320,
        xaxis=dict(showgrid=True, gridcolor="rgba(59,130,246,0.1)"), yaxis=dict(showgrid=False)
    )
    fig_cat.update_traces(textposition="outside", textfont=dict(color=customer_color))
    st.plotly_chart(fig_cat, use_container_width=True)
    
    # Recorder breakdown (only if data has a recorder column)
    all_recorders = []
    for df in sheets.values():
        rec_col = [c for c in df.columns if "recorded" in c.lower()]
        if rec_col:
            all_recorders.extend(df[rec_col[0]].dropna().astype(str).str.strip().tolist())
    
    if all_recorders:
        st.markdown('<div class="section-header">👤 Issues by Recorder</div>', unsafe_allow_html=True)
        recorder_counts = pd.Series(all_recorders).value_counts().reset_index()
        recorder_counts.columns = ["Recorder", "Issues Logged"]
        fig_rec = px.bar(recorder_counts, x="Recorder", y="Issues Logged",
                         color="Issues Logged", color_continuous_scale=["#2d2d5e", customer_color], text="Issues Logged")
        fig_rec.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"), showlegend=False, coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0), height=300,
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(59,130,246,0.1)")
        )
        fig_rec.update_traces(textposition="outside", textfont=dict(color="#60a5fa"))
        st.plotly_chart(fig_rec, use_container_width=True)
    
    # All data tables
    st.markdown('<div class="section-header">📑 All Issues by Category</div>', unsafe_allow_html=True)
    any_data = False
    for name, df in sheets.items():
        if len(df) > 0:
            any_data = True
            icon = CATEGORY_ICONS.get(name, "📄")
            with st.expander(f"{icon} {name.strip()} — {len(df)} issue(s)", expanded=False):
                st.dataframe(df, use_container_width=True, hide_index=True)
    if not any_data:
        st.info("No issues found for the current customer / month filter.")


# ========== TOTAL DOWNTIME VIEW ==========
elif st.session_state.active_view == "total_downtime":
    st.markdown(f"""
    <div class="main-header">
        <h1>⏱️ Downtime Insights</h1>
        <p>Total accumulated downtime across all categories — {total_downtime_str}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Back to Home"):
        st.session_state.active_view = "home"
        st.rerun()

    st.markdown("---")

    # Downtime per category (minutes)
    cat_downtime = {}
    for name, df in sheets.items():
        dur_col = [c for c in df.columns if "duration" in c.lower()]
        if dur_col and len(df) > 0:
            mins = df[dur_col[0]].apply(parse_duration_to_minutes)
            cat_downtime[name.strip()] = int(mins.sum())

    has_downtime = any(v > 0 for v in cat_downtime.values())

    if not has_downtime:
        st.info("No duration/downtime data is available for this customer or the selected month filter. "
                "Downtime is calculated from a column containing 'duration' in its name.")
    else:
        # KPIs
        total_dt_min = sum(cat_downtime.values())
        worst_cat = max(cat_downtime, key=cat_downtime.get)
        avg_per_issue = round(total_dt_min / total_issues, 1) if total_issues else 0
        k1, k2, k3 = st.columns(3)
        k1.metric("Total Downtime", total_downtime_str)
        k2.metric("Highest Downtime Category", worst_cat, f"{cat_downtime[worst_cat]:,} min")
        k3.metric("Avg Downtime / Issue", f"{avg_per_issue} min")

        st.markdown("---")

        # Downtime by category chart
        st.markdown('<div class="section-header">⏱️ Downtime by Category (hours)</div>', unsafe_allow_html=True)
        dt_df = pd.DataFrame(
            [(k, round(v / 60, 1)) for k, v in cat_downtime.items() if v > 0],
            columns=["Category", "Hours"]
        ).sort_values("Hours", ascending=True)
        fig_dt = px.bar(dt_df, x="Hours", y="Category", orientation="h",
                        color="Hours", color_continuous_scale=["#1e293b", "#a78bfa"], text="Hours")
        fig_dt.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"), showlegend=False, coloraxis_showscale=False,
            margin=dict(l=0, r=20, t=10, b=0), height=320,
            xaxis=dict(showgrid=True, gridcolor="rgba(59,130,246,0.1)"), yaxis=dict(showgrid=False)
        )
        fig_dt.update_traces(textposition="outside", textfont=dict(color="#a78bfa"))
        st.plotly_chart(fig_dt, use_container_width=True)

        # Downtime by OPCO
        opco_downtime = {}
        for name, df in sheets.items():
            dur_col = [c for c in df.columns if "duration" in c.lower()]
            opco_col = [c for c in df.columns if "opco" in c.lower()]
            if dur_col and opco_col and len(df) > 0:
                for _, row in df.iterrows():
                    mins = parse_duration_to_minutes(row[dur_col[0]])
                    if mins <= 0:
                        continue
                    for opco in normalize_opcos(str(row[opco_col[0]]), all_individual_opcos):
                        opco_downtime[opco] = opco_downtime.get(opco, 0) + mins

        if opco_downtime:
            st.markdown('<div class="section-header">🌍 Downtime by OPCO (hours)</div>', unsafe_allow_html=True)
            opco_dt_df = pd.DataFrame(
                [(k, round(v / 60, 1)) for k, v in opco_downtime.items()],
                columns=["OPCO", "Hours"]
            ).sort_values("Hours", ascending=False)
            fig_odt = px.bar(opco_dt_df, x="OPCO", y="Hours",
                             color="Hours", color_continuous_scale=["#1e3a5f", customer_color], text="Hours")
            fig_odt.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"), showlegend=False, coloraxis_showscale=False,
                margin=dict(l=0, r=0, t=10, b=0), height=320,
                xaxis=dict(showgrid=False, tickangle=-45),
                yaxis=dict(showgrid=True, gridcolor="rgba(59,130,246,0.1)")
            )
            fig_odt.update_traces(textposition="outside", textfont=dict(color=customer_color))
            st.plotly_chart(fig_odt, use_container_width=True)


# ========== CATEGORIES VIEW ==========
elif st.session_state.active_view == "categories":
    st.markdown(f"""
    <div class="main-header">
        <h1>📂 All Categories</h1>
        <p>{len(non_empty_sheets)} active categories with issues</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("← Back to Home"):
        st.session_state.active_view = "home"
        st.rerun()
    
    st.markdown("---")
    
    chart_data = pd.DataFrame({
        "Category": [k.strip() for k in sheets.keys()],
        "Count": [len(v) for v in sheets.values()]
    }).sort_values("Count", ascending=False)
    
    fig = px.bar(chart_data, x="Category", y="Count",
                 color="Count", color_continuous_scale=["#1e3a5f", customer_color], text="Count")
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"), showlegend=False, coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=10, b=0), height=350,
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(59,130,246,0.1)")
    )
    fig.update_traces(textposition="outside", textfont=dict(color=customer_color))
    st.plotly_chart(fig, use_container_width=True)
    
    # Clickable category buttons
    st.markdown('<div class="section-header">📋 Select a Category</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (name, df) in enumerate(sheets.items()):
        with cols[i % 4]:
            icon = CATEGORY_ICONS.get(name, "📄")
            if st.button(f"{icon}\n\n**{len(df)} issues**\n\n{name.strip()}", key=f"catview_{name}", use_container_width=True):
                st.session_state.active_view = f"sheet_{name}"
                st.rerun()


# ========== TOP CATEGORY VIEW ==========
elif st.session_state.active_view == "top_category":
    name = top_category[0]
    df = top_category[1]
    icon = CATEGORY_ICONS.get(name, "📄")
    color = CATEGORY_COLORS.get(name, customer_color)
    
    st.markdown(f"""
    <div class="main-header">
        <h1>🔥 Top Category: {icon} {name.strip()}</h1>
        <p>Highest issue count — {len(df)} issues</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("← Back to Home"):
        st.session_state.active_view = "home"
        st.rerun()
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Issues", len(df))
    col2.metric("Data Fields", len(df.columns))
    rec_col = [c for c in df.columns if "recorded" in c.lower()]
    if rec_col:
        col3.metric("Recorders", df[rec_col[0]].dropna().nunique())
    
    # OPCO breakdown
    opco_col = [c for c in df.columns if "opco" in c.lower()]
    prio_col = [c for c in df.columns if "priority" in c.lower()]
    chart_l, chart_r = st.columns(2)

    with chart_l:
        if opco_col:
            st.markdown('<div class="section-header">🌍 By OPCO</div>', unsafe_allow_html=True)
            opco_list = []
            for val in df[opco_col[0]].dropna():
                opco_list.extend(normalize_opcos(str(val), all_individual_opcos))
            opco_data = pd.Series(opco_list).value_counts().reset_index()
            opco_data.columns = ["OPCO", "Count"]
            fig = px.pie(opco_data, values="Count", names="OPCO",
                         color_discrete_sequence=px.colors.sequential.Tealgrn, hole=0.3)
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"), margin=dict(l=0, r=0, t=10, b=0), height=300
            )
            st.plotly_chart(fig, use_container_width=True)

    with chart_r:
        # Priority distribution (falls back to any low-cardinality column)
        cat_col = prio_col[0] if prio_col else None
        if not cat_col:
            skip = set([c for c in df.columns if any(k in c.lower() for k in
                        ["date", "time", "no.", "number", "statement", "rca", "description", "title", "duration"])])
            candidates = [c for c in df.columns
                          if c not in skip and 1 < df[c].nunique(dropna=True) <= 15]
            cat_col = candidates[0] if candidates else None
        if cat_col:
            st.markdown(f'<div class="section-header">📊 By {cat_col}</div>', unsafe_allow_html=True)
            pdata = df[cat_col].astype(str).str.strip().value_counts().reset_index()
            pdata.columns = [cat_col, "Count"]
            figp = px.bar(pdata, x=cat_col, y="Count", color="Count",
                          color_continuous_scale=["#1e3a5f", color], text="Count")
            figp.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"), showlegend=False, coloraxis_showscale=False,
                margin=dict(l=0, r=0, t=10, b=0), height=300,
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(59,130,246,0.1)")
            )
            figp.update_traces(textposition="outside", textfont=dict(color=color))
            st.plotly_chart(figp, use_container_width=True)
    
    # Data table
    st.markdown('<div class="section-header">📊 All Issues</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)


# ========== OPCOs VIEW ==========
elif st.session_state.active_view == "opcos":
    st.markdown(f"""
    <div class="main-header">
        <h1>🌍 OPCOs Affected</h1>
        <p>{len(all_opcos)} unique OPCOs with reported issues</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("← Back to Home"):
        st.session_state.active_view = "home"
        st.rerun()
    
    st.markdown("---")
    
    # OPCO issue count
    opco_issue_counts = {}
    for name, df in sheets.items():
        opco_col = [c for c in df.columns if "opco" in c.lower()]
        if opco_col:
            for _, row in df.iterrows():
                raw_opco = str(row[opco_col[0]]).strip()
                if raw_opco and raw_opco != "nan":
                    for opco in normalize_opcos(raw_opco, all_individual_opcos):
                        opco_issue_counts[opco] = opco_issue_counts.get(opco, 0) + 1
    
    if opco_issue_counts:
        opco_df = pd.DataFrame(list(opco_issue_counts.items()), columns=["OPCO", "Issues"])
        opco_df = opco_df.sort_values("Issues", ascending=False)

        c_bar, c_donut = st.columns([3, 2])
        with c_bar:
            st.markdown('<div class="section-header">📊 Issues by OPCO</div>', unsafe_allow_html=True)
            fig = px.bar(opco_df, x="OPCO", y="Issues", color="Issues",
                         color_continuous_scale=["#1e3a5f", customer_color], text="Issues")
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"), showlegend=False, coloraxis_showscale=False,
                margin=dict(l=0, r=0, t=10, b=0), height=350,
                xaxis=dict(showgrid=False, tickangle=-45),
                yaxis=dict(showgrid=True, gridcolor="rgba(59,130,246,0.1)")
            )
            fig.update_traces(textposition="outside", textfont=dict(color=customer_color))
            st.plotly_chart(fig, use_container_width=True)
        with c_donut:
            st.markdown('<div class="section-header">🍩 Share</div>', unsafe_allow_html=True)
            fig_d = px.pie(opco_df, values="Issues", names="OPCO",
                           color_discrete_sequence=px.colors.sequential.Tealgrn, hole=0.4)
            fig_d.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"), margin=dict(l=0, r=0, t=10, b=0),
                height=350, showlegend=False
            )
            fig_d.update_traces(textinfo="percent", textfont=dict(color="white"))
            st.plotly_chart(fig_d, use_container_width=True)
    
    # OPCO selector
    if all_opcos:
        st.markdown('<div class="section-header">🔍 Select an OPCO for Details</div>', unsafe_allow_html=True)
        selected_opco = st.selectbox("Choose OPCO", sorted(all_opcos))
        
        if selected_opco:
            st.markdown(f'<div class="section-header">📋 Issues for: {selected_opco}</div>', unsafe_allow_html=True)
            for name, df in sheets.items():
                opco_col = [c for c in df.columns if "opco" in c.lower()]
                if opco_col:
                    opco_filtered = df[df[opco_col[0]].astype(str).apply(
                        lambda x: selected_opco in normalize_opcos(x, all_individual_opcos)
                    )]
                    if not opco_filtered.empty:
                        icon = CATEGORY_ICONS.get(name, "📄")
                        with st.expander(f"{icon} {name.strip()} — {len(opco_filtered)} issue(s)", expanded=True):
                            st.dataframe(opco_filtered, use_container_width=True, hide_index=True)
    else:
        st.info("No OPCO data available for this customer.")


# ========== INDIVIDUAL SHEET VIEW ==========
elif st.session_state.active_view.startswith("sheet_"):
    sheet_name = st.session_state.active_view.replace("sheet_", "")
    df = sheets[sheet_name]
    icon = CATEGORY_ICONS.get(sheet_name, "📄")
    color = CATEGORY_COLORS.get(sheet_name, customer_color)
    
    st.markdown(f"""
    <div class="main-header">
        <h1>{icon} {sheet_name.strip()}</h1>
        <p>Detailed view — {len(df)} issue(s)</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("← Back to Home"):
        st.session_state.active_view = "home"
        st.rerun()
    
    st.markdown("---")
    
    if len(df) == 0:
        st.info("No issues recorded in this category.")
    else:
        # KPIs
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Issues", len(df))
        col2.metric("Data Fields", len(df.columns))
        rec_col = [c for c in df.columns if "recorded" in c.lower()]
        if rec_col:
            col3.metric("Recorders", df[rec_col[0]].dropna().nunique())
        else:
            col3.metric("Recorders", "N/A")
        
        st.markdown("---")
        
        # Filters
        st.markdown('<div class="section-header">🔍 Filters</div>', unsafe_allow_html=True)
        filter_cols = st.columns(3)
        filtered_df = df.copy()
        
        filterable_columns = [col for col in df.columns if df[col].dtype == "object" and 1 < df[col].nunique() <= 20]
        
        for i, col in enumerate(filterable_columns[:3]):
            with filter_cols[i % 3]:
                unique_vals = ["All"] + sorted([str(v) for v in df[col].dropna().unique()])
                selected = st.selectbox(f"{col}", unique_vals, key=f"filter_{sheet_name}_{col}")
                if selected != "All":
                    filtered_df = filtered_df[filtered_df[col].astype(str) == selected]
        
        # Charts
        if len(df) > 1:
            col_l, col_r = st.columns(2)
            
            if rec_col:
                with col_l:
                    st.markdown('<div class="section-header">👤 By Recorder</div>', unsafe_allow_html=True)
                    rec_data = filtered_df[rec_col[0]].value_counts().reset_index()
                    rec_data.columns = ["Recorder", "Count"]
                    fig = px.pie(rec_data, values="Count", names="Recorder",
                                color_discrete_sequence=px.colors.sequential.Tealgrn, hole=0.3)
                    fig.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#94a3b8"), margin=dict(l=0, r=0, t=10, b=0), height=250
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            opco_col = [c for c in df.columns if "opco" in c.lower()]
            if opco_col:
                with col_r:
                    st.markdown('<div class="section-header">🌍 By OPCO</div>', unsafe_allow_html=True)
                    # Split combined OPCOs and count individually
                    opco_list = []
                    for val in filtered_df[opco_col[0]].dropna():
                        opco_list.extend(normalize_opcos(str(val), all_individual_opcos))
                    opco_data = pd.Series(opco_list).value_counts().reset_index()
                    opco_data.columns = ["OPCO", "Count"]
                    fig2 = px.bar(opco_data, x="OPCO", y="Count", color="Count",
                                 color_continuous_scale=["#1e3a5f", color], text="Count")
                    fig2.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#94a3b8"), showlegend=False, coloraxis_showscale=False,
                        margin=dict(l=0, r=0, t=10, b=0), height=250,
                        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(59,130,246,0.1)")
                    )
                    fig2.update_traces(textposition="outside", textfont=dict(color=color))
                    st.plotly_chart(fig2, use_container_width=True)
        
        # Data table
        st.markdown('<div class="section-header">📊 Issue Details</div>', unsafe_allow_html=True)
        st.dataframe(filtered_df, use_container_width=True, hide_index=True,
                     height=min(500, (len(filtered_df) + 1) * 50))
        
        # Download
        st.markdown("---")
        col_dl1, col_dl2, _ = st.columns([1, 1, 3])
        with col_dl1:
            csv = filtered_df.to_csv(index=False)
            st.download_button("📥 Download CSV", data=csv,
                              file_name=f"{sheet_name.strip()}.csv", mime="text/csv", use_container_width=True)
        with col_dl2:
            st.download_button("📥 Download Excel", data=open(excel_path, "rb").read(),
                              file_name=os.path.basename(excel_path),
                              mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                              use_container_width=True)
