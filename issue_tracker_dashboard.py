import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="GNOC Issue Tracker",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 50%, #24243e 100%);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1e3f 0%, #2d2d5e 100%);
        border-right: 1px solid #4a4a8a;
    }
    .kpi-card {
        background: linear-gradient(135deg, #1e1e3f 0%, #2d2d5e 100%);
        border: 1px solid #4a4a8a;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #00d4ff;
    }
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00d4ff;
        margin: 5px 0;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #a0a0c0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .kpi-icon {
        font-size: 1.5rem;
        margin-bottom: 5px;
    }
    .main-header {
        text-align: center;
        padding: 20px 0;
        margin-bottom: 20px;
    }
    .main-header h1 {
        color: #00d4ff;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    .main-header p {
        color: #a0a0c0;
        font-size: 1.1rem;
        margin-top: 5px;
    }
    .section-header {
        color: #ffffff;
        border-bottom: 2px solid #00d4ff;
        padding-bottom: 8px;
        margin: 30px 0 15px 0;
        font-size: 1.3rem;
    }
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e1e3f 0%, #2d2d5e 100%);
        border: 1px solid #4a4a8a;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    [data-testid="stMetricValue"] {
        color: #00d4ff;
    }
    hr {
        border-color: #4a4a8a;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #1e1e3f 0%, #2d2d5e 100%) !important;
        border: 1px solid #4a4a8a !important;
        border-radius: 8px !important;
        padding: 8px 20px !important;
        color: white !important;
        transition: all 0.3s !important;
        min-height: 0px !important;
        max-height: 40px !important;
        font-size: 0.8rem !important;
        white-space: nowrap !important;
    }
    .stButton > button:hover {
        border-color: #00d4ff !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,212,255,0.3) !important;
    }
    .stButton > button:active, .stButton > button:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 15px rgba(0,212,255,0.5) !important;
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
    "MSDP Issue": "#ff6b6b",
    "Autocaller Issue": "#ffa726",
    "Test Alerts Issue": "#ffee58",
    "Auto TT Issue": "#66bb6a",
    "ITSM Issue": "#42a5f5",
    "OneFM Issue ": "#ab47bc",
    "EtigerNG Issue ": "#26c6da"
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

# ===== HEADER WITH CUSTOMER BUTTONS =====
header_col1, header_col2, header_col3 = st.columns([1, 3, 1.5])

with header_col2:
    st.markdown("""
    <div style="text-align: center; padding-top: 5px;">
        <h1 style="color: #00d4ff; margin-bottom: 0; font-size: 2.5rem;">🛡️ GNOC Issue Tracker</h1>
    </div>
    """, unsafe_allow_html=True)

with header_col3:
    if st.button("🔵 Airtel Africa / OBF", key="btn_aa", use_container_width=True):
        st.session_state.selected_customer = "🔵 Airtel Africa / OBF"
        st.session_state.active_view = "home"
        st.rerun()
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

sheets = load_all_sheets(excel_path)
customer_color = customer_config["color"]

# Show which customer is selected
st.markdown(f"""
<div style="text-align: center; margin-bottom: 20px;">
    <span style="background: {customer_color}22; border: 1px solid {customer_color}; 
                 padding: 5px 20px; border-radius: 20px; color: {customer_color};
                 font-weight: 600; font-size: 0.9rem;">
        Viewing: {selected_customer}
    </span>
</div>
""", unsafe_allow_html=True)

# Compute global stats
total_issues = sum(len(df) for df in sheets.values())
non_empty_sheets = {k: v for k, v in sheets.items() if len(v) > 0}
top_category = max(sheets.items(), key=lambda x: len(x[1])) if sheets else ("N/A", pd.DataFrame())

# OPCO normalization mappings
OPCO_ALIASES = {
    "Africa": "South Africa",
}
# OPCOs to expand to all individual OPCOs
OPCO_EXPAND_ALL = {"ALL MTN"}


def get_all_individual_opcos(sheets_data):
    """Get all individual OPCOs (excluding ALL MTN and Africa alias)."""
    opcos = set()
    for df in sheets_data.values():
        opco_col = [c for c in df.columns if "opco" in c.lower()]
        if opco_col:
            for val in df[opco_col[0]].dropna().str.strip().unique():
                for o in str(val).split(","):
                    o = o.strip()
                    if o and o not in OPCO_EXPAND_ALL:
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
        if o in OPCO_EXPAND_ALL:
            result.extend(all_individual_opcos)
        else:
            o = OPCO_ALIASES.get(o, o)
            result.append(o)
    return result


# Get all individual OPCOs for expansion
all_individual_opcos = get_all_individual_opcos(sheets)

all_opcos = set()
for name, df in sheets.items():
    opco_col = [c for c in df.columns if "opco" in c.lower()]
    if opco_col:
        for val in df[opco_col[0]].dropna().str.strip().unique():
            all_opcos.update(normalize_opcos(val, all_individual_opcos))

# Sidebar
with st.sidebar:
    st.markdown(f"## 🛡️ {selected_customer}")
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
        <p style="color: #a0a0c0;">Click any card below to drill down into details</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Clickable KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(f"📊\n\n**{total_issues}**\n\nTOTAL ISSUES", key="kpi_total"):
            st.session_state.active_view = "total_issues"
            st.rerun()
    
    with col2:
        if st.button(f"📂\n\n**{len(non_empty_sheets)}**\n\nACTIVE CATEGORIES", key="kpi_cat"):
            st.session_state.active_view = "categories"
            st.rerun()
    
    with col3:
        if st.button(f"🔥\n\n**{len(top_category[1])}**\n\nTOP CATEGORY", key="kpi_top"):
            st.session_state.active_view = "top_category"
            st.rerun()
    
    with col4:
        if st.button(f"🌍\n\n**{len(all_opcos)}**\n\nOPCOs AFFECTED", key="kpi_opco"):
            st.session_state.active_view = "opcos"
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
                     color="Count", color_continuous_scale=["#1e3a5f", customer_color], text="Count")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#a0a0c0"), showlegend=False, coloraxis_showscale=False,
            margin=dict(l=0, r=20, t=10, b=0), height=300,
            xaxis=dict(showgrid=True, gridcolor="rgba(74,74,138,0.3)"), yaxis=dict(showgrid=False)
        )
        fig.update_traces(textposition="outside", textfont=dict(color=customer_color))
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
                font=dict(color="#a0a0c0"), margin=dict(l=0, r=0, t=10, b=0),
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
            font=dict(color="#a0a0c0"), showlegend=False, coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0), height=300,
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(74,74,138,0.3)")
        )
        fig_rec.update_traces(textposition="outside", textfont=dict(color=customer_color))
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
        font=dict(color="#a0a0c0"), showlegend=False, coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=10, b=0), height=350,
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(74,74,138,0.3)")
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
            font=dict(color="#a0a0c0"), margin=dict(l=0, r=0, t=10, b=0), height=300
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
            font=dict(color="#a0a0c0"), showlegend=False, coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0), height=350,
            xaxis=dict(showgrid=False, tickangle=-45),
            yaxis=dict(showgrid=True, gridcolor="rgba(74,74,138,0.3)")
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
                        font=dict(color="#a0a0c0"), margin=dict(l=0, r=0, t=10, b=0), height=250
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
                        font=dict(color="#a0a0c0"), showlegend=False, coloraxis_showscale=False,
                        margin=dict(l=0, r=0, t=10, b=0), height=250,
                        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(74,74,138,0.3)")
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
