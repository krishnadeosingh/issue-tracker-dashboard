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

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 50%, #24243e 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1e3f 0%, #2d2d5e 100%);
        border-right: 1px solid #4a4a8a;
    }
    
    /* KPI Cards */
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
    
    /* Header styling */
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
    
    /* Section headers */
    .section-header {
        color: #ffffff;
        border-bottom: 2px solid #00d4ff;
        padding-bottom: 8px;
        margin: 30px 0 15px 0;
        font-size: 1.3rem;
    }
    
    /* Status badges */
    .status-open {
        background: #ff4b4b;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-resolved {
        background: #00c853;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e1e3f;
        border-radius: 8px;
        padding: 10px 20px;
        color: #a0a0c0;
        border: 1px solid #4a4a8a;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00d4ff !important;
        color: #0f0c29 !important;
    }
    
    /* Metric styling */
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
    
    /* Divider */
    hr {
        border-color: #4a4a8a;
    }
</style>
""", unsafe_allow_html=True)

# Load data
EXCEL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Issue Tracker M.xlsx")


@st.cache_data
def load_all_sheets():
    xlsx = pd.ExcelFile(EXCEL_FILE)
    sheets = {}
    for name in xlsx.sheet_names:
        df = pd.read_excel(xlsx, sheet_name=name)
        sheets[name] = df
    return sheets


sheets = load_all_sheets()

# Category colors
CATEGORY_COLORS = {
    "MSDP Issue": "#ff6b6b",
    "Autocaller Issue": "#ffa726",
    "Test Alerts Issue": "#ffee58",
    "Auto TT Issue": "#66bb6a",
    "ITSM Issue": "#42a5f5",
    "OneFM Issue ": "#ab47bc",
    "EtigerNG Issue ": "#26c6da"
}

# Category icons
CATEGORY_ICONS = {
    "MSDP Issue": "🔴",
    "Autocaller Issue": "📞",
    "Test Alerts Issue": "⚠️",
    "Auto TT Issue": "🎫",
    "ITSM Issue": "🔧",
    "OneFM Issue ": "📡",
    "EtigerNG Issue ": "🖥️"
}

# Sidebar
with st.sidebar:
    st.markdown("## 🛡️ GNOC Issue Tracker")
    st.markdown("---")
    
    view_mode = st.radio(
        "📌 Navigation",
        ["Overall Dashboard", "Individual Category"],
        label_visibility="collapsed"
    )
    
    if view_mode == "Individual Category":
        selected_sheet = st.selectbox(
            "Select Category",
            list(sheets.keys()),
            format_func=lambda x: f"{CATEGORY_ICONS.get(x, '📄')} {x}"
        )
    
    st.markdown("---")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%d %b %Y, %H:%M')}")
    st.markdown(f"**Total Issues:** {sum(len(df) for df in sheets.values())}")


# ========== OVERALL DASHBOARD ==========
if view_mode == "Overall Dashboard":
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ GNOC Issue Tracker Dashboard</h1>
        <p>Real-time monitoring of operational issues across all categories</p>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Row
    total_issues = sum(len(df) for df in sheets.values())
    top_category = max(sheets.items(), key=lambda x: len(x[1]))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">📊</div>
            <div class="kpi-value">{total_issues}</div>
            <div class="kpi-label">Total Issues</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">📂</div>
            <div class="kpi-value">{len(sheets)}</div>
            <div class="kpi-label">Categories</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">🔥</div>
            <div class="kpi-value">{len(top_category[1])}</div>
            <div class="kpi-label">Top Category Issues</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Count unique OPCOs across all sheets
        all_opcos = set()
        for df in sheets.values():
            opco_col = [c for c in df.columns if "opco" in c.lower()]
            if opco_col:
                all_opcos.update(df[opco_col[0]].dropna().unique())
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">🌍</div>
            <div class="kpi-value">{len(all_opcos)}</div>
            <div class="kpi-label">OPCOs Affected</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts Row
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="section-header">📊 Issues by Category</div>', unsafe_allow_html=True)
        
        chart_data = pd.DataFrame({
            "Category": [k.strip() for k in sheets.keys()],
            "Count": [len(v) for v in sheets.values()]
        }).sort_values("Count", ascending=True)
        
        fig = px.bar(
            chart_data, 
            x="Count", 
            y="Category", 
            orientation="h",
            color="Count",
            color_continuous_scale=["#1e3a5f", "#00d4ff"],
            text="Count"
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#a0a0c0"),
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=20, t=10, b=0),
            height=300,
            xaxis=dict(showgrid=True, gridcolor="rgba(74,74,138,0.3)"),
            yaxis=dict(showgrid=False)
        )
        fig.update_traces(textposition="outside", textfont=dict(color="#00d4ff"))
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.markdown('<div class="section-header">🍩 Distribution</div>', unsafe_allow_html=True)
        
        pie_data = pd.DataFrame({
            "Category": [k.strip() for k in sheets.keys()],
            "Count": [len(v) for v in sheets.values()]
        })
        
        fig_pie = px.pie(
            pie_data,
            values="Count",
            names="Category",
            color_discrete_sequence=list(CATEGORY_COLORS.values()),
            hole=0.4
        )
        fig_pie.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#a0a0c0"),
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
            legend=dict(font=dict(size=10))
        )
        fig_pie.update_traces(textinfo="percent+value", textfont=dict(color="white"))
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Recorder stats
    st.markdown('<div class="section-header">👤 Issues by Recorder</div>', unsafe_allow_html=True)
    
    all_recorders = []
    for df in sheets.values():
        rec_col = [c for c in df.columns if "recorded" in c.lower()]
        if rec_col:
            all_recorders.extend(df[rec_col[0]].dropna().str.strip().tolist())
    
    if all_recorders:
        recorder_counts = pd.Series(all_recorders).value_counts().reset_index()
        recorder_counts.columns = ["Recorder", "Issues Logged"]
        
        fig_rec = px.bar(
            recorder_counts,
            x="Recorder",
            y="Issues Logged",
            color="Issues Logged",
            color_continuous_scale=["#2d2d5e", "#00d4ff"],
            text="Issues Logged"
        )
        fig_rec.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#a0a0c0"),
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0),
            height=250,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(74,74,138,0.3)")
        )
        fig_rec.update_traces(textposition="outside", textfont=dict(color="#00d4ff"))
        st.plotly_chart(fig_rec, use_container_width=True)
    
    # Category cards
    st.markdown('<div class="section-header">📋 Category Overview</div>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    for i, (name, df) in enumerate(sheets.items()):
        with cols[i % 4]:
            icon = CATEGORY_ICONS.get(name, "📄")
            color = CATEGORY_COLORS.get(name, "#00d4ff")
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e1e3f, #2d2d5e); 
                        border: 1px solid {color}; border-radius: 10px; 
                        padding: 15px; margin-bottom: 10px; text-align: center;
                        border-left: 4px solid {color};">
                <div style="font-size: 1.5rem;">{icon}</div>
                <div style="color: {color}; font-size: 1.5rem; font-weight: 700;">{len(df)}</div>
                <div style="color: #a0a0c0; font-size: 0.8rem;">{name.strip()}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Expandable data tables
    st.markdown('<div class="section-header">📑 Detailed Data</div>', unsafe_allow_html=True)
    
    for name, df in sheets.items():
        icon = CATEGORY_ICONS.get(name, "📄")
        with st.expander(f"{icon} {name.strip()} — {len(df)} issue(s)", expanded=False):
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=min(400, (len(df) + 1) * 50)
            )


# ========== INDIVIDUAL CATEGORY VIEW ==========
else:
    df = sheets[selected_sheet]
    icon = CATEGORY_ICONS.get(selected_sheet, "📄")
    color = CATEGORY_COLORS.get(selected_sheet, "#00d4ff")
    
    # Header
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: {color}; font-size: 2rem;">{icon} {selected_sheet.strip()}</h1>
        <p style="color: #a0a0c0;">Detailed view of all issues in this category</p>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI row
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Issues", len(df))
    col2.metric("Data Fields", len(df.columns))
    
    # Count unique recorders
    rec_col = [c for c in df.columns if "recorded" in c.lower()]
    if rec_col:
        unique_recs = df[rec_col[0]].dropna().nunique()
        col3.metric("Recorders", unique_recs)
    else:
        col3.metric("Recorders", "N/A")
    
    st.markdown("---")
    
    # Filters
    st.markdown('<div class="section-header">🔍 Filters</div>', unsafe_allow_html=True)
    
    filter_cols = st.columns(3)
    filtered_df = df.copy()
    
    filterable_columns = []
    for col in df.columns:
        if df[col].dtype == "object" and 1 < df[col].nunique() <= 20:
            filterable_columns.append(col)
    
    for i, col in enumerate(filterable_columns[:3]):
        with filter_cols[i % 3]:
            unique_vals = ["All"] + sorted([str(v) for v in df[col].dropna().unique()])
            selected = st.selectbox(f"{col}", unique_vals, key=f"filter_{selected_sheet}_{col}")
            if selected != "All":
                filtered_df = filtered_df[filtered_df[col].astype(str) == selected]
    
    # Stats charts for individual view
    if rec_col and len(df) > 1:
        col_l, col_r = st.columns(2)
        
        with col_l:
            st.markdown('<div class="section-header">👤 By Recorder</div>', unsafe_allow_html=True)
            rec_data = filtered_df[rec_col[0]].value_counts().reset_index()
            rec_data.columns = ["Recorder", "Count"]
            fig = px.pie(rec_data, values="Count", names="Recorder", 
                        color_discrete_sequence=px.colors.sequential.Tealgrn,
                        hole=0.3)
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#a0a0c0"),
                margin=dict(l=0, r=0, t=10, b=0),
                height=250
            )
            st.plotly_chart(fig, use_container_width=True)
        
        opco_col = [c for c in df.columns if "opco" in c.lower()]
        if opco_col:
            with col_r:
                st.markdown('<div class="section-header">🌍 By OPCO</div>', unsafe_allow_html=True)
                opco_data = filtered_df[opco_col[0]].value_counts().reset_index()
                opco_data.columns = ["OPCO", "Count"]
                fig2 = px.bar(opco_data, x="OPCO", y="Count", 
                             color="Count",
                             color_continuous_scale=["#1e3a5f", color],
                             text="Count")
                fig2.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#a0a0c0"),
                    showlegend=False,
                    coloraxis_showscale=False,
                    margin=dict(l=0, r=0, t=10, b=0),
                    height=250,
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor="rgba(74,74,138,0.3)")
                )
                fig2.update_traces(textposition="outside", textfont=dict(color=color))
                st.plotly_chart(fig2, use_container_width=True)
    
    # Data table
    st.markdown('<div class="section-header">📊 Issue Details</div>', unsafe_allow_html=True)
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        height=min(500, (len(filtered_df) + 1) * 50)
    )
    
    # Download
    st.markdown("---")
    col_dl1, col_dl2, _ = st.columns([1, 1, 3])
    with col_dl1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"{selected_sheet.strip()}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_dl2:
        st.download_button(
            label="📥 Download Excel",
            data=open(EXCEL_FILE, "rb").read(),
            file_name="Issue Tracker M.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
