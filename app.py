import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="E-Commerce Customer Segmentation Dashboard",
    layout="wide",
    page_icon="🛍️"
)

st.title("🛍️ E-Commerce Customer Segmentation Dashboard")
st.markdown("""
Analyze customer behavior based on **Recency, Frequency, and Monetary** values  
and view **K-Means clustering results** interactively.
""")


uploaded_file = st.file_uploader("📂 Upload your clustered_output.csv file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    df.columns = df.columns.str.strip().str.lower()

    cluster_col = None
    possible_names = ["cluster", "prediction", "segment", "group"]
    for name in possible_names:
        if name in df.columns:
            cluster_col = name
            break

    if cluster_col is None:
        st.error("⚠️ No cluster column found! Please upload the correct clustered_output.csv file.")
        st.stop()

    st.subheader("📊 Data Preview")
    st.dataframe(df.head(), use_container_width=True)

    st.markdown("### 📈 Dataset Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", df["customerid"].nunique() if "customerid" in df.columns else len(df))
    col2.metric("Average Recency", round(df["recency"].mean(), 2))
    col3.metric("Average Frequency", round(df["frequency"].mean(), 2))
    col4.metric("Average Monetary", f"${df['monetary'].mean():,.2f}")

    st.markdown("### 🎯 Cluster Distribution")
    cluster_counts = df[cluster_col].value_counts().reset_index()
    cluster_counts.columns = ["Cluster", "Count"]

    fig_pie = px.pie(
        cluster_counts,
        values="Count",
        names="Cluster",
        title="Customer Distribution by Cluster",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("### 📊 Cluster Averages (RFM Metrics)")
    cluster_summary = df.groupby(cluster_col)[["recency", "frequency", "monetary"]].mean().reset_index()

    fig_bar = px.bar(
        cluster_summary,
        x=cluster_col,
        y=["recency", "frequency", "monetary"],
        barmode="group",
        title="Average RFM per Cluster",
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("### 🌐 3D Cluster Visualization (RFM Space)")
    fig_3d = px.scatter_3d(
        df,
        x="recency", y="frequency", z="monetary",
        color=cluster_col,
        hover_data=["customerid"] if "customerid" in df.columns else None,
        color_discrete_sequence=px.colors.qualitative.Bold,
        title="Customer Segmentation (3D View)"
    )
    st.plotly_chart(fig_3d, use_container_width=True)

    st.markdown("### 🔍 Filter Customers by Cluster")
    selected_cluster = st.selectbox("Select Cluster to View:", sorted(df[cluster_col].unique()))
    filtered = df[df[cluster_col] == selected_cluster]
    st.dataframe(filtered, use_container_width=True)

    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv,
        file_name=f"cluster_{selected_cluster}_customers.csv",
        mime="text/csv",
    )

else:
    st.info("👆 Upload your `clustered_output.csv` to view the dashboard.")








