
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.dashboard.config import SEGMENT_COLORS

def render_stakeholder_view(filtered_df, metrics):
    st.markdown("## ♟️ Executive Boardroom: Strategic Hub")
    st.markdown("---")
    
    # Section 1: Strategic Pulse (KPI Scorecard on steroids)
    st.markdown("### 📡 Strategic Pulse")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Revenue Impact",
            value=f"${metrics['total_revenue']:,.0f}",
            delta=f"{metrics['retention_rate']:.1f}% Retention",
            help="Total revenue generated from analyzed customer segments"
        )
        
    with col2:
        vip_rev = filtered_df[filtered_df['segment_name'] == 'Champions']['Monetary'].sum()
        st.metric(
            label="Champions Capitalization",
            value=f"${vip_rev:,.0f}",
            delta=f"{(vip_rev/metrics['total_revenue']*100):.1f}% of Total",
            help="Revenue contribution from Champions segment"
        )
        
    with col3:
        risk_rev = filtered_df[filtered_df['segment_name'] == 'Needs Attention']['Monetary'].sum()
        st.metric(
            label="Capital at Risk",
            value=f"${risk_rev:,.0f}",
            delta=f"-{(risk_rev/metrics['total_revenue']*100):.1f}% Exposure",
            delta_color="inverse",
            help="Potential revenue loss from Needs Attention segment"
        )
        
    with col4:
        # Simple projected growth metric
        projected = metrics['total_revenue'] * 1.15
        st.metric(
            label="Proj. Q4 Revenue (+15%)",
            value=f"${projected:,.0f}",
            delta="Target",
            help="Projected revenue based on current trajectory"
        )

    st.markdown("---")
    
    # Section 2: ROI Scenario Simulator
    st.markdown("### 🎲 Strategic Scenario Simulator")
    st.info("💡 **Interactive Tool**: Adjust investments below to simulate business outcomes.")
    
    sim_col1, sim_col2 = st.columns([1, 2])
    
    with sim_col1:
        st.markdown("#### Investment Variables")
        
        invest_retention = st.slider("Retention Investment ($)", 0, 50000, 10000, step=1000, help="Budget for win-back campaigns")
        invest_acquisition = st.slider("Acquisition Investment ($)", 0, 100000, 20000, step=5000, help="Budget for new user ads")
        expected_conversion = st.slider("Expected Conversion Lift (%)", 0.0, 10.0, 2.5, step=0.1)
        churn_reduction_goal = st.slider("Target Churn Reduction (%)", 0.0, 20.0, 5.0, step=0.5)
        
    with sim_col2:
        st.markdown("#### Projected ROI Analysis")
        
        # Simple logical simulation
        current_rev = metrics['total_revenue']
        
        # ROI Logic
        # Retention: Every $1k saves 0.5% of At-Risk Revenue (capped)
        at_risk_pool = filtered_df[filtered_df['segment_name'] == 'Needs Attention']['Monetary'].sum()
        saved_revenue = min(at_risk_pool, (invest_retention / 1000) * (at_risk_pool * 0.05)) # Heuristic
        saved_revenue = saved_revenue * (churn_reduction_goal / 5.0) # Scale by goal confidence
        
        # Acquisition: Each $100 brings 1 customer with Avg LTV
        avg_ltv = metrics['avg_order_value'] * metrics['avg_lifespan_months'] # Approx LTV
        new_customers = (invest_acquisition / 100) * (1 + expected_conversion/100)
        new_revenue = new_customers * avg_ltv
        
        total_projected_rev = current_rev + saved_revenue + new_revenue
        total_cost = invest_retention + invest_acquisition
        net_profit = total_projected_rev - current_rev - total_cost
        roi_pct = (net_profit / total_cost * 100) if total_cost > 0 else 0
        
        # Visualize
        fig_waterfall = go.Figure(go.Waterfall(
            name = "20", orientation = "v",
            measure = ["relative", "relative", "relative", "total"],
            x = ["Current Revenue", "Retained Capital", "New Acquisition", "Projected Total"],
            textposition = "outside",
            text = [f"${current_rev/1000:.0f}k", f"+${saved_revenue/1000:.0f}k", f"+${new_revenue/1000:.0f}k", f"${total_projected_rev/1000:.0f}k"],
            y = [current_rev, saved_revenue, new_revenue, total_projected_rev],
            connector = {"line":{"color":"rgb(63, 63, 63)"}},
        ))
        
        fig_waterfall.update_layout(
            title = "Projected Revenue Bridge",
            showlegend = False,
            height=400
        )
        st.plotly_chart(fig_waterfall, use_container_width=True)
        
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.success(f"💰 **Net Profit Impact**: ${net_profit:,.0f}")
        with res_col2:
            st.metric("ROI", f"{roi_pct:.1f}%", delta="Positive" if roi_pct > 0 else "Negative")

    st.markdown("---")
    
    # Section 3: NLP-style Health Report
    st.markdown("### 📝 Smart Business Report")
    
    report_container = st.container()
    
    # Logic to generate text
    dominant_segment = filtered_df['segment_name'].mode()[0]
    highest_spender = filtered_df.loc[filtered_df['Monetary'].idxmax()]
    
    with report_container:
        st.markdown(f"""
        <div class="info-panel" style="background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);">
            <h4>Executive Summary Generated on {pd.Timestamp.now().strftime('%Y-%m-%d')}</h4>
            <ul>
                <li><strong>Dominant Customer Profile:</strong> The majority of your active user base falls into the <b>{dominant_segment}</b> category.</li>
                <li><strong>Revenue Concentration:</strong> The top 20% of customers are contributing <b>{(filtered_df.nlargest(int(len(filtered_df)*0.2), 'Monetary')['Monetary'].sum() / metrics['total_revenue'] * 100):.1f}%</b> of total revenue.</li>
                <li><strong>Retention Alert:</strong> With a retention rate of <b>{metrics['retention_rate']:.1f}%</b>, { "we are performing well above industry standards." if metrics['retention_rate'] > 80 else "investment in loyalty plays is recommended."}</li>
                <li><strong>Top Performer:</strong> Customer <b>#{highest_spender['CustomerID']}</b> is the highest value asset with <b>${highest_spender['Monetary']:,.0f}</b> LTV.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
