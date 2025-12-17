
import pandas as pd
import streamlit as st
import numpy as np
from src.dashboard.config import FILE_PATH, SEGMENT_COL, SEGMENT_MAP

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(FILE_PATH)
        df.columns = df.columns.str.strip()
        df['segment_name'] = df[SEGMENT_COL].map(SEGMENT_MAP)
        return df
    except Exception as e:
        st.error(f"❌ Data loading failed: {e}")
        return None

@st.cache_data
def calculate_business_metrics(df):
    """Calculate all business metrics with caching"""
    total_customers = len(df)
    total_revenue = df["Monetary"].sum()
    avg_order_value = df["Monetary"].mean()
    churn_rate = (df["churn"].sum() / len(df)) * 100
    retention_rate = 100 - churn_rate
    avg_lifespan_months = df["Frequency"].mean() * 6
    customer_satisfaction = 100 - (df["Returns"].mean() * 10 + df["SupportTickets"].mean() * 5)
    engagement_score = (df["AvgSessionTime"].mean() + df["ReferralCount"].mean() * 10) / 2

    return {
        'total_customers': total_customers,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'churn_rate': churn_rate,
        'retention_rate': retention_rate,
        'avg_lifespan_months': avg_lifespan_months,
        'customer_satisfaction': customer_satisfaction,
        'engagement_score': engagement_score
    }

@st.cache_data
def calculate_segment_metrics(df):
    """Calculate segment-wise metrics with caching"""
    metrics = df.groupby("segment_name").agg({
        "Monetary": ["sum", "mean", "count"],
        "Frequency": "mean",
        "Recency": "mean",
        "Returns": "mean",
        "SupportTickets": "mean",
        "AvgSessionTime": "mean",
        "ReferralCount": "mean",
        "churn": "mean",
        "LoyaltyScore": "mean" 
    }).round(2)
    
    # Flatten columns
    metrics.columns = ["_".join(col).strip() for col in metrics.columns.values]
    return metrics.reset_index()
