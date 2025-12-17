
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from src.dashboard.config import SEGMENT_COLORS, RECOMMENDATIONS
from src.dashboard.components.charts import create_sankey_diagram, create_retention_curve

def render_deep_dive(filtered_df):
    st.markdown("---")
    st.markdown("## 🔍 Strategic Problem Solving & Deep Dive")
    
    # NEW: Real-World Problem Visualizations
    st.markdown("### 🧩 Churn Diagnosis & Customer Flow")
    st.markdown("Understanding *where* and *why* we lose customers.")
    
    prob_col1, prob_col2 = st.columns([1.5, 1])
    
    with prob_col1:
        # Problem 1: Flow Analysis
        st.plotly_chart(create_sankey_diagram(filtered_df), use_container_width=True, key="deep_dive_sankey")
        st.caption("👈 **Problem Solved:** Identifies the exact path from Segment to Churn. Visualizes if 'Low Loyalty' is the primary leakage point.")
        
    with prob_col2:
        # Problem 2: Timing
        st.plotly_chart(create_retention_curve(filtered_df), use_container_width=True, key="deep_dive_retention")
        st.caption("👈 **Problem Solved:** Pinpoints the 'Danger Zone' (in days) where most customers drop off. Use this to time your email campaigns.")

    st.markdown("---")
    st.markdown("### 🔬 Metric Correlations & Growth Drivers")
    insight_tab1, insight_tab2, insight_tab3 = st.tabs(["📈 Revenue Analytics", "🎯 Risk Assessment", "🚀 Growth Strategies"])
    
    with insight_tab1: # Revenue
        col1, col2 = st.columns(2)
        with col1:
            rev_by_seg = filtered_df.groupby("segment_name")["Monetary"].sum().reset_index()
            fig = px.bar(rev_by_seg, x="segment_name", y="Monetary", color="segment_name", color_discrete_map=SEGMENT_COLORS, title="💰 Revenue Distribution")
            fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            # Pareto
            sorted_cust = filtered_df.sort_values("Monetary", ascending=False)
            sorted_cust["cumulative_revenue"] = sorted_cust["Monetary"].cumsum()
            total_rev = sorted_cust["Monetary"].sum()
            sorted_cust["cumulative_percentage"] = (sorted_cust["cumulative_revenue"] / total_rev) * 100
            sorted_cust["customer_percentage"] = (np.arange(len(sorted_cust))) / len(sorted_cust) * 100
            
            fig_pareto = px.line(sorted_cust, x="customer_percentage", y="cumulative_percentage", title="📊 Revenue Variability Analysis (Pareto)")
            fig_pareto.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
            st.plotly_chart(fig_pareto, use_container_width=True)
            
    with insight_tab2: # Risk
        col1, col2 = st.columns(2)
        with col1:
             # Heatmap
             recency_bins = pd.cut(filtered_df["Recency"], bins=5).astype(str)
             freq_bins = pd.cut(filtered_df["Frequency"], bins=5).astype(str)
             
             # Create a safe copy for pivot
             df_pivot = pd.DataFrame({
                 'churn_probability': filtered_df['churn_probability'].values,
                 'Recency_Bin': recency_bins,
                 'Frequency_Bin': freq_bins
             })
             
             churn_matrix = pd.pivot_table(df_pivot, values='churn_probability', index='Recency_Bin', columns='Frequency_Bin', aggfunc='mean')
             fig_map = px.imshow(churn_matrix, title="🔥 Churn Risk Heatmap", labels=dict(x="Freq", y="Recency", color="Risk"))
             fig_map.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
             st.plotly_chart(fig_map, use_container_width=True)
        with col2:
             fig_risk = px.scatter(filtered_df, x="churn_probability", y="Monetary", color="segment_name", color_discrete_map=SEGMENT_COLORS, size="Frequency", title="⚠️ Risk vs Value")
             fig_risk.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
             st.plotly_chart(fig_risk, use_container_width=True)
             
    with insight_tab3: # Growth
        col1, col2 = st.columns(2)
        with col1:
            growth = filtered_df.groupby("segment_name").agg({"ReferralCount": "mean", "AvgSessionTime": "mean", "LoyaltyScore": "mean"}).reset_index()
            growth["score"] = growth["ReferralCount"]*0.4 + growth["AvgSessionTime"]*0.3 + growth["LoyaltyScore"]*0.3
            fig_growth = px.bar(growth, x="segment_name", y="score", color="segment_name", color_discrete_map=SEGMENT_COLORS, title="🚀 Growth Potential")
            fig_growth.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
            st.plotly_chart(fig_growth, use_container_width=True)
        with col2:
             fig_loyalty = px.scatter(filtered_df, x="LoyaltyScore", y="AvgSessionTime", size="Monetary", color="segment_name", color_discrete_map=SEGMENT_COLORS, title="😊 Loyalty vs Engagement")
             fig_loyalty.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
             st.plotly_chart(fig_loyalty, use_container_width=True)
             
    # Customer Drill Down
    st.markdown("### 🔍 Customer Deep Dive & Segmentation")
    if st.checkbox("Show Advanced Customer Analysis"):
         analysis_type = st.radio("Analysis Type:", ["Top Customers", "At-Risk Analysis", "Segment Comparison"], horizontal=True)
         
         if analysis_type == "Top Customers":
             top_n = st.slider("Number of top customers:", 10, 50, 20)
             st.dataframe(filtered_df.nlargest(top_n, "Monetary").style.background_gradient(cmap='Greens', subset=['Monetary']))
         elif analysis_type == "At-Risk Analysis":
             thresh = st.slider("Churn Threshold:", 0.0, 1.0, 0.7)
             st.dataframe(filtered_df[filtered_df["churn_probability"] > thresh].style.background_gradient(cmap='Reds', subset=['churn_probability']))
         else:
             metric = st.selectbox("Compare:", ["Monetary", "Frequency", "LoyaltyScore"])
             fig = px.box(filtered_df, x="segment_name", y=metric, color="segment_name", color_discrete_map=SEGMENT_COLORS, title=f"Comparison: {metric}")
             fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
             st.plotly_chart(fig, use_container_width=True)

def render_recommendations_section(selected_segment):
    st.markdown("---")
    st.markdown("## 🧠 AI-Powered Business Recommendations")
    
    if selected_segment != "All Segments":
        rec = RECOMMENDATIONS.get(selected_segment, {})
        if rec:
            st.markdown(f"### {rec['priority']} Priority: {selected_segment}")
            st.markdown(f"**Expected Business Impact:** {rec['expected_impact']}")
            st.markdown("#### 🎯 Recommended Actions:")
            for action in rec['actions']:
                st.markdown(f"• {action}")
            
            # Score
            priority_score = {"🔥 HIGH": 95, "⚡ MEDIUM-HIGH": 80, "🚨 CRITICAL": 90, "📈 MEDIUM": 60}
            score = priority_score.get(rec['priority'], 70)
            st.progress(score/100)
            st.caption(f"Action Priority Score: {score}/100")
        else:
            st.info("Select a specific segment to see tailored recommendations")
    else:
        st.info("💡 Select a specific customer segment from the sidebar to see AI-powered recommendations and action plans!")

def render_footer():
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: #b8c5d1; background: linear-gradient(135deg, #0f1419 0%, #1a1a2e 100%); border-radius: 15px; margin-top: 30px;">
        <h3 style="color: #ffffff; margin-bottom: 10px;">🎯 Customer Intelligence Hub</h3>
        <p style="margin: 5px 0; font-size: 0.9em;">Built with ❤️ using PySpark & Streamlit</p>
        <p style="margin: 5px 0; font-size: 0.8em; opacity: 0.7;">Advanced Customer Segmentation & Analytics Platform v2.0</p>
        <p style="margin: 5px 0; font-size: 0.8em; opacity: 0.7;">© 2024 | Transforming Data into Business Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
