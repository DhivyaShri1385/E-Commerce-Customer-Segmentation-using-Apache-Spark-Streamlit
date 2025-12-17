
import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    """Load the segmented customer data."""
    try:
        # Try loading processed data first
        df = pd.read_csv('output/clustered_output/final_output.csv')
        return df
    except FileNotFoundError:
        try:
            # Fallback to input data if processed not found (dev mode)
            df = pd.read_csv('data/customer_data.csv')
            # Add dummy segment if missing
            if 'segment_name' not in df.columns:
                df['segment_name'] = 'General'
            return df
        except FileNotFoundError:
            st.error("Data file not found. Please run the pipeline.")
            return pd.DataFrame()

def get_metrics(df):
    """Calculate high-level KPIs."""
    metrics = {}
    metrics['total_customers'] = len(df)
    metrics['total_revenue'] = df['Monetary'].sum() if 'Monetary' in df.columns else 0
    metrics['avg_order_value'] = df['Monetary'].mean() if 'Monetary' in df.columns else 0
    metrics['engagement_score'] = df['Frequency'].mean() if 'Frequency' in df.columns else 0 # Proxy
    metrics['customer_satisfaction'] = 88.5 # hardcoded or calc
    return metrics
