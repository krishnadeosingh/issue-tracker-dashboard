import streamlit as st
import pandas as pd

# Page config
st.set_page_config(
    page_title="Issue Tracker Dashboard",
    page_icon="📋",
    layout="wide"
)

# Load data
import os
EXCEL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Issue Tracker M.xlsx")


@st.cache_data
def load_all_sheets():
    """Load all sheets from the Excel file."""
    xlsx = pd.ExcelFile(EXCEL_FILE)
    sheets = {}
    for name in xlsx.sheet_names:
        df = pd.read_excel(xlsx, sheet_name=name)
        sheets[name] = df
    return sheets


# Load data
sheets = load_all_sheets()

# Title
st.title("📋 Issue Tracker Dashboard")
st.markdown("---")

# Sidebar navigation
st.sidebar.title("Navigation")
view_options = ["🏠 Overall View"] + [f"📄 {name}" for name in sheets.keys()]
selected_view = st.sidebar.radio("Select View", view_options)

# --- OVERALL VIEW ---
if selected_view == "🏠 Overall View":
    st.header("Overall Summary")

    # Summary metrics
    total_issues = sum(len(df) for df in sheets.values())
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Issues", total_issues)
    col2.metric("Total Sheets", len(sheets))
    col3.metric("Categories", len(sheets))

    st.markdown("---")

    # Issues per sheet bar chart
    st.subheader("Issues by Category")
    summary_data = pd.DataFrame({
        "Category": list(sheets.keys()),
        "Issue Count": [len(df) for df in sheets.values()]
    })
    st.bar_chart(summary_data.set_index("Category"))

    st.markdown("---")

    # Summary table
    st.subheader("Sheet-wise Breakdown")
    summary_table = []
    for name, df in sheets.items():
        cols = df.columns.tolist()
        summary_table.append({
            "Sheet Name": name,
            "Number of Issues": len(df),
            "Columns": ", ".join(cols[:5]) + ("..." if len(cols) > 5 else "")
        })
    st.dataframe(pd.DataFrame(summary_table), use_container_width=True, hide_index=True)

    st.markdown("---")

    # Quick preview of each sheet
    st.subheader("Quick Preview (All Sheets)")
    for name, df in sheets.items():
        with st.expander(f"📄 {name} ({len(df)} issues)", expanded=False):
            st.dataframe(df, use_container_width=True, hide_index=True)

# --- INDIVIDUAL SHEET VIEW ---
else:
    # Extract sheet name from selection
    sheet_name = selected_view.replace("📄 ", "")
    df = sheets[sheet_name]

    st.header(f"📄 {sheet_name}")
    st.markdown(f"**Total Records:** {len(df)}")
    st.markdown("---")

    # Metrics row
    col1, col2 = st.columns(2)
    col1.metric("Total Issues", len(df))
    col2.metric("Columns", len(df.columns))

    st.markdown("---")

    # Filters
    st.subheader("🔍 Filters")
    filter_cols = st.columns(3)

    filtered_df = df.copy()

    # Add filters for key columns if they exist
    filterable_columns = []
    for col in df.columns:
        if df[col].dtype == "object" and df[col].nunique() <= 20 and df[col].nunique() > 1:
            filterable_columns.append(col)

    for i, col in enumerate(filterable_columns[:3]):
        with filter_cols[i % 3]:
            unique_vals = ["All"] + sorted(
                [str(v) for v in df[col].dropna().unique()]
            )
            selected = st.selectbox(f"{col}", unique_vals, key=f"filter_{sheet_name}_{col}")
            if selected != "All":
                filtered_df = filtered_df[filtered_df[col].astype(str) == selected]

    st.markdown("---")

    # Display data
    st.subheader("📊 Data Table")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    # Download button
    st.markdown("---")
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"{sheet_name}.csv",
        mime="text/csv"
    )
