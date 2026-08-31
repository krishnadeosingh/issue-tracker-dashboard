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
        padding: 24px 20px;
        text-align: center;
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
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
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 8px 0;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .kpi-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    .kpi-icon {
        font-size: 1.5rem;
        margin-bottom: 5px;
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
        sheets[name] = df
    return sheets


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
            options=["All"] + [str(y) for y in all_years],
            index=0,
            key="year_filter"
        )
    with mn_col:
        if selected_year == "All":
            month_options = ["All"]
        else:
            available_months = sorted([m for y, m in all_dates if y == int(selected_year)])
            month_options = ["All"] + [month_names[m - 1] for m in available_months]
        selected_month_name = st.selectbox(
            "📅 Month",
            options=month_options,
            index=0,
            key="month_filter"
        )

# Filter sheets by selected year and month
if selected_year == "All":
    sheets = sheets_raw
else:
    filter_year = int(selected_year)
    filter_month = month_names.index(selected_month_name) + 1 if selected_month_name != "All" else None
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
total_downtime_str = f"{total_hours}h {remaining_mins}m"

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
    
    # Clickable KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(f"📊 Total Issues: {total_issues}", key="kpi_total"):
            st.session_state.active_view = "total_issues"
            st.rerun()
    
    with col2:
        if st.button(f"⏱️ Total Downtime: {total_downtime_str}", key="kpi_downtime"):
            st.session_state.active_view = "total_issues"
            st.rerun()
    
    with col3:
        if st.button(f"🌍 Most Affected: {most_affected_opco} ({most_affected_opco_count})", key="kpi_opco"):
            st.session_state.active_view = "opcos"
            st.rerun()
    
    with col4:
        if st.button(f"🔥 Top: {top_category[0].strip()} ({len(top_category[1])})", key="kpi_top"):
            st.session_state.active_view = "top_category"
            st.rerun()
    
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
    
    # Recorder breakdown
    st.markdown('<div class="section-header">👤 Issues by Recorder</div>', unsafe_allow_html=True)
    all_recorders = []
    for df in sheets.values():
        rec_col = [c for c in df.columns if "recorded" in c.lower()]
        if rec_col:
            all_recorders.extend(df[rec_col[0]].dropna().str.strip().tolist())
    
    if all_recorders:
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
    for name, df in sheets.items():
        if len(df) > 0:
            icon = CATEGORY_ICONS.get(name, "📄")
            with st.expander(f"{icon} {name.strip()} — {len(df)} issue(s)", expanded=True):
                st.dataframe(df, use_container_width=True, hide_index=True)


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
