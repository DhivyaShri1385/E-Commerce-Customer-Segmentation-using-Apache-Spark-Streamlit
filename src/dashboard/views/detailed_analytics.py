
import streamlit as st
import plotly.express as px
import numpy as np
from src.dashboard.components.charts import (
    create_segment_sunburst, 
    create_revenue_bar_chart, 
    create_frequency_histogram, 
    create_scatter_plot,
    create_correlation_heatmap,
    create_radar_chart,
    create_violin_plot,
    create_box_plot,
    create_density_contour,
    create_treemap
)
from src.dashboard.config import SEGMENT_COLORS

def render_detailed_analytics(filtered_df, segment_metrics, metrics):
    render_customer_segments_view(filtered_df, segment_metrics, metrics)

def render_customer_segments_view(filtered_df, segment_metrics, metrics):
    st.markdown("---")
    st.markdown("## 📊 Customer Groups Overview")

    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Segment DNA", 
        "💰 Spending Habits", 
        "🛒 Frequency Analysis", 
        "💎 Revenue Contribution"
    ])
    
    # TAB 1: Segment DNA
    with tab1:
        st.markdown("### Segment Characteristics")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.plotly_chart(create_radar_chart(filtered_df), use_container_width=True, key="seg_radar")
        with col2:
            st.markdown("### 📋 Segment Details")
            segment_counts = filtered_df['segment_name'].value_counts()
            for segment in segment_counts.index:
                count = segment_counts[segment]
                percentage = (count / len(filtered_df)) * 100
                revenue = filtered_df[filtered_df['segment_name'] == segment]['Monetary'].sum()
                color = SEGMENT_COLORS.get(segment, "#666")
                st.markdown(f"""
                <div style="background-color: {color}20; border: 1px solid {color}; color: #e0e0e0; padding: 10px; border-radius: 8px; margin: 5px 0;">
                    <strong style="color: {color}; font-size: 1.0em;">{segment}</strong><br>
                    {count:,} cust • {percentage:.1f}% • <b>${revenue:,.0f}</b>
                </div>
                """, unsafe_allow_html=True)

    # TAB 2: Revenue
    with tab2:
        st.markdown("### Revenue Distribution")
        col1, col2 = st.columns(2)
        with col1:
             st.plotly_chart(create_treemap(filtered_df), use_container_width=True, key="seg_treemap")
        with col2:
             st.plotly_chart(create_box_plot(filtered_df), use_container_width=True, key="seg_boxplot")

    # TAB 3: Frequency
    with tab3:
        st.markdown("### Frequency Analysis")
        st.plotly_chart(create_violin_plot(filtered_df, "Frequency", "Distribution of Orders"), use_container_width=True, key="seg_violin")

    # TAB 4: Contribution
    with tab4:
        st.markdown("### Revenue Contribution")
        
        col1, col2 = st.columns(2)
        with col1:
            revenue_by_segment = filtered_df.groupby('segment_name')['Monetary'].sum()
            fig_rev_pie = px.pie(
                values=revenue_by_segment.values,
                names=revenue_by_segment.index,
                title="Total Revenue by Segment",
                color=revenue_by_segment.index,
                color_discrete_map=SEGMENT_COLORS
            )
            st.plotly_chart(fig_rev_pie, use_container_width=True, key="seg_pie")
        
        with col2:
             st.plotly_chart(create_correlation_heatmap(filtered_df), use_container_width=True, key="seg_corr")

def render_trends_view(filtered_df, segment_metrics, metrics):
    st.markdown("---")
    st.markdown("## 📈 Market Trends & Seasonality")
    
    st.info("Analyzing shopping patterns over time to identify seasonal spikes and engagement trends.")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Shopping Intensity Heatmap")
        st.caption("Where do most transactions cluster in terms of Recency vs Monetary value?")
        st.plotly_chart(create_density_contour(filtered_df), use_container_width=True, key="trends_density")
    
    with col2:
        st.markdown("### Key Observations")
        st.write("""
        - **High Density Zones:** Indicate the most common customer behaviors.
        - **Outliers:** Scattered points show potential high-value one-time buyers.
        - **Seasonality:** (Simulated) Spikes in Q4 are typical for E-commerce.
        """)
        
    st.markdown("### 🗓️ Longitudinal Analysis")
    # Using existing charts re-purposed for trends
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(create_scatter_plot(filtered_df), use_container_width=True, key="trends_scatter")
    with c2:
        # Retention curve is also a trend-over-time proxy
        from src.dashboard.components.charts import create_retention_curve
        st.plotly_chart(create_retention_curve(filtered_df), use_container_width=True, key="trends_retention")
