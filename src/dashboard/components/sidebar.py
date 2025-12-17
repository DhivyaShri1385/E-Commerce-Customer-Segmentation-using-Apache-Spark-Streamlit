
import streamlit as st
import requests

def render_sidebar(df):
    """
    Renders the sidebar and returns the filtered dataframe and filter parameters.
    """
    st.sidebar.title("🎯 Customer Intelligence Hub")
    st.sidebar.markdown("---")

    # Quick Filters
    st.sidebar.subheader("🔍 Quick Filters")
    # Handling potential None or empty dataframe if data loading failed or just started
    if df is None or df.empty:
        return None, "All Segments"
        
    segment_options = ["All Segments"] + sorted(df['segment_name'].unique().tolist())
    selected_segment = st.sidebar.selectbox(
        "Focus Segment",
        segment_options,
        help="Filter dashboard to specific customer segment"
    )

    # Advanced Filters (collapsed by default for performance)
    with st.sidebar.expander("⚙️ Advanced Filters", expanded=False):
        max_recency = int(df["Recency"].max()) if not df.empty else 365
        max_monetary = float(df["Monetary"].max()) if not df.empty else 1000.0
        
        recency_range = st.slider("Recency (days)", 0, max_recency, (0, 365))
        monetary_range = st.slider("Monetary Value ($)", 0.0, max_monetary, (0.0, max_monetary))
        loyalty_filter = st.slider("Min Loyalty Score", 0, 100, 0)

    # Apply filters efficiently
    filtered_df = df.copy()
    if selected_segment != "All Segments":
        filtered_df = filtered_df[filtered_df['segment_name'] == selected_segment]

    filtered_df = filtered_df[
        (filtered_df["Recency"] >= recency_range[0]) &
        (filtered_df["Recency"] <= recency_range[1]) &
        (filtered_df["Monetary"] >= monetary_range[0]) &
        (filtered_df["Monetary"] <= monetary_range[1]) &
        (filtered_df["LoyaltyScore"] >= loyalty_filter)
    ]
    
    # Spark UI check
    check_spark_status()

    return filtered_df, selected_segment

def check_spark_status():
    spark_ui = None
    for port in range(4040, 4050):
        try:
            r = requests.get(f"http://localhost:{port}", timeout=0.1)
            if r.status_code == 200:
                spark_ui = f"http://localhost:{port}"
                break
        except:
            continue

    if spark_ui:
        st.sidebar.success("✅ Spark Engine Active")
        st.sidebar.markdown(f"[🔗 Spark Monitoring]({spark_ui})")
    else:
        st.sidebar.warning("⚠️ Spark Engine Offline")
