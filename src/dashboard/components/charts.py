
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import pandas as pd
import numpy as np
from src.dashboard.config import SEGMENT_COLORS, SEGMENT_ALIASES

# COMMON LAYOUT THEME
def apply_theme(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#E5E7EB', # Platinum White for Premium Dark
        font_family="Outfit",
        title_font_size=20,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    fig.update_xaxes(showgrid=False, zeroline=False, color='#9CA3AF') # Cool Gray
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.08)', zeroline=False, color='#9CA3AF')
    return fig

@st.cache_data
def create_segment_sunburst(df):
    """
    Hierarchical Sunburst: Segment -> Churn Status
    """
    # Create hierarchy data
    df['churn_label'] = df['churn'].apply(lambda x: "Did Churn" if x == 1 else "Retained")
    
    fig = px.sunburst(
        df,
        path=['segment_name', 'churn_label'],
        values='Monetary',
        color='segment_name',
        color_discrete_map=SEGMENT_COLORS,
        title="Revenue Hierarchy: Segment » Retention Status"
    )
    fig.update_traces(textinfo="label+percent entry")
    return apply_theme(fig)

@st.cache_data
def create_radar_chart(df):
    """
    Radar Chart comparing average metrics across segments.
    """
    # Normalize data for radar chart (0-1 scale)
    metrics = ["Recency", "Frequency", "Monetary", "LoyaltyScore", "AvgSessionTime"]
    
    # Calculate means
    seg_means = df.groupby("segment_name")[metrics].mean()
    
    # Min-Max Scaling
    normalized = (seg_means - seg_means.min()) / (seg_means.max() - seg_means.min())
    normalized = normalized.reset_index()
    
    fig = go.Figure()
    
    for i, row in normalized.iterrows():
        segment = row['segment_name']
        color = SEGMENT_COLORS.get(segment, '#fff')
        
        fig.add_trace(go.Scatterpolar(
            r=row[metrics].values,
            theta=metrics,
            fill='toself',
            name=segment,
            line_color=color,
            opacity=0.7
        ))
        
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], showticklabels=False, linecolor='#333'),
            bgcolor='rgba(0,0,0,0)'
        ),
        title="Segment DNA Profile (Normalized Metrics)"
    )
    return apply_theme(fig)

@st.cache_data
def create_revenue_bar_chart(df):
    """
    Robust Revenue Bar Chart
    Handles multiple column schemas: ['Monetary_sum'] or ['Total Revenue']
    """
    # 1. Identify Value Column
    value_col = None
    candidates = ['Total Revenue', 'Monetary_sum', 'Monetary']
    
    for c in candidates:
        if c in df.columns:
            value_col = c
            break
            
    if not value_col:
        # Fallback: Search for any column with "Revenue" or "Monetary"
        for c in df.columns:
            if 'Revenue' in c or 'Monetary' in c:
                value_col = c
                break
    
    if not value_col:
        # User requested: "if data is not available create it"
        # If we really can't find a column, use the first numeric one or mock it
        numeric_cols = df.select_dtypes(include=np.number).columns
        if len(numeric_cols) > 0:
            value_col = numeric_cols[0]
        else:
            df['Estimated Revenue'] = np.random.randint(1000, 5000, size=len(df))
            value_col = 'Estimated Revenue'

    # 2. Identify Segment Column
    seg_col = 'segment_name' if 'segment_name' in df.columns else 'Segment'
    if seg_col not in df.columns:
        # Create dummy segments if missing
        df['Segment'] = [f"Segment {i}" for i in range(len(df))]
        seg_col = 'Segment'

    revenue_data = df.sort_values(by=value_col, ascending=True)
    
    fig = px.bar(
        revenue_data,
        x=value_col,
        y=seg_col,
        orientation='h',
        title="Revenue by Customer Segment",
        color=seg_col,
        color_discrete_map=SEGMENT_COLORS,
        text_auto='.2s'
    )
    fig.update_traces(marker_line_width=0, opacity=0.9)
    return apply_theme(fig)

@st.cache_data
def create_frequency_histogram(df):
    fig = px.histogram(
        df,
        x="Frequency",
        color="segment_name",
        title="Purchase Frequency Distribution",
        color_discrete_map=SEGMENT_COLORS,
        barmode='overlay',
        opacity=0.75,
        marginal="box" # Adds neat boxplot on top
    )
    return apply_theme(fig)

@st.cache_data
def create_scatter_plot(df):
    fig = px.scatter(
        df,
        x="Recency",
        y="Frequency",
        size="Monetary",
        color="segment_name",
        title="RFM Galaxy Map",
        color_discrete_map=SEGMENT_COLORS,
        size_max=25,
        hover_data=['CustomerID']
    )
    # Glow effect
    fig.update_traces(marker=dict(line=dict(width=1, color='White')))
    return apply_theme(fig)

@st.cache_data
def create_correlation_heatmap(df):
    numeric_cols = ["Recency", "Frequency", "Monetary", "LoyaltyScore", "AvgSessionTime", "churn_probability"]
    corr_matrix = df[numeric_cols].corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu', # Red-Blue diverging
        zmid=0
    ))
    fig.update_layout(title="Correlation Matrix")
    return apply_theme(fig)

@st.cache_data
def create_sankey_diagram(df):
    """
    Sankey showing flow from Segment -> Loyalty Level -> Churn Status
    """
    # Create nodes
    # Level 1: Segments
    # Level 2: Loyalty (High/Low)
    # Level 3: Churn (Stay/risk)
    
    # 1. Define Categories
    df['Loyalty_Level'] = df['LoyaltyScore'].apply(lambda x: 'High Loyalty' if x > 50 else 'Low Loyalty')
    df['Status'] = df['churn'].apply(lambda x: 'Churned' if x == 1 else 'Active')
    
    # Aggregation
    sankey_data = df.groupby(['segment_name', 'Loyalty_Level', 'Status']).size().reset_index(name='count')
    
    # Sources and Targets
    labels = list(df['segment_name'].unique()) + \
             list(df['Loyalty_Level'].unique()) + \
             list(df['Status'].unique())
             
    label_map = {label: i for i, label in enumerate(labels)}
    
    sources = []
    targets = []
    values = []
    
    # Flow 1: Segment -> Loyalty
    flow1 = df.groupby(['segment_name', 'Loyalty_Level']).size().reset_index(name='count')
    for _, row in flow1.iterrows():
        sources.append(label_map[row['segment_name']])
        targets.append(label_map[row['Loyalty_Level']])
        values.append(row['count'])
        
    # Flow 2: Loyalty -> Status
    flow2 = df.groupby(['Loyalty_Level', 'Status']).size().reset_index(name='count')
    for _, row in flow2.iterrows():
        sources.append(label_map[row['Loyalty_Level']])
        targets.append(label_map[row['Status']])
        values.append(row['count'])
        
    # Colors
    node_colors = [SEGMENT_COLORS.get(l, "#888") for l in labels]
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=15,
            line=dict(color="black", width=0.5),
            label=labels,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color='rgba(127, 0, 255, 0.2)' # Translucent purple
        )
    )])
    
    fig.update_layout(title="Customer Journey Flow: Segment » Loyalty » Retention", font_size=12)
    return apply_theme(fig)

@st.cache_data
def create_retention_curve(df):
    """
    Simulated Survival Analysis (Retention over Tenure/Recency)
    """
    # Use Recency as a proxy for 'Time until drop off'
    # We group by Recency (buckets) and count active users
    
    hist_data = df[df['churn']==0]['Recency']
    
    # Cumulative distribution
    hist, bins = np.histogram(hist_data, bins=50)
    cdf = np.cumsum(hist)
    survival = 1 - (cdf / cdf[-1])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=bins[:-1], 
        y=survival*100, 
        mode='lines', 
        name='Survival Probability',
        fill='tozeroy',
        line=dict(color='#00F5FF', width=3)
    ))
    
    fig.update_layout(
        title="Customer Survival Curve (Retention vs Days Since Purchase)",
        xaxis_title="Days Since Last Purchase",
        yaxis_title="Probability of Retention (%)",
        showlegend=False
    )
    return apply_theme(fig)

@st.cache_data
def create_treemap(df):
    """
    Treemap: Segment Size (Area) vs Revenue (Color)
    Uses 'Revenue' Context Aliases
    """
    # Map Labels
    df_temp = df.copy()
    df_temp['display_label'] = df_temp['segment_name'].map(SEGMENT_ALIASES.get("Revenue", {}))
    df_temp['display_label'] = df_temp['display_label'].fillna(df_temp['segment_name'])
    
    # Map Colors keys to new labels for consistency
    color_map_new = {v: SEGMENT_COLORS.get(k, "#333") for k, v in SEGMENT_ALIASES.get("Revenue", {}).items()}
    
    fig = px.treemap(
        df_temp,
        path=[px.Constant("All Revenue Sources"), 'display_label'],
        values='Monetary',
        color='display_label',
        color_discrete_map=color_map_new,
        title="Revenue Hierarchy (TreeMap)"
    )
    fig.update_traces(textinfo="label+value+percent entry")
    return apply_theme(fig)

@st.cache_data
def create_violin_plot(df, metric, title):
    """
    Violin plot using 'Activity' Context Aliases
    """
    # Map Labels
    df_temp = df.copy()
    df_temp['display_label'] = df_temp['segment_name'].map(SEGMENT_ALIASES.get("Activity", {}))
    df_temp['display_label'] = df_temp['display_label'].fillna(df_temp['segment_name'])
    
    color_map_new = {v: SEGMENT_COLORS.get(k, "#333") for k, v in SEGMENT_ALIASES.get("Activity", {}).items()}

    fig = px.violin(
        df_temp,
        y=metric,
        x="display_label",
        color="display_label",
        box=True, 
        points="all",
        title=title,
        color_discrete_map=color_map_new
    )
    return apply_theme(fig)

@st.cache_data
def create_funnel_chart(df):
    """
    Funnel Chart: Count of users by Risk Level
    """
    # count by segment
    counts = df['segment_name'].value_counts().reset_index()
    counts.columns = ['segment', 'count']
    
    # Map to Risk labels
    risk_map = SEGMENT_ALIASES.get("Risk", {})
    counts['label'] = counts['segment'].map(risk_map)
    counts['color'] = counts['segment'].map(SEGMENT_COLORS)
    
    # Sort for funnel shape (usually largest to smallest, but here we group logically if needed)
    counts = counts.sort_values('count', ascending=False)
    
    fig = px.funnel(
        counts, 
        x='count', 
        y='label', 
        color='segment', # Maintain original keys for color mapping if simple
        color_discrete_map=SEGMENT_COLORS,
        title="Customer Risk Funnel"
    )
    return apply_theme(fig)

@st.cache_data
def create_box_plot(df):
    """
    Box plot for Monetary value (Handling outliers).
    """
    fig = px.box(
        df,
        x="segment_name",
        y="Monetary",
        color="segment_name",
        title="Monetary Value Distribution (Spread & Outliers)",
        color_discrete_map=SEGMENT_COLORS,
        notched=True
    )
    return apply_theme(fig)

@st.cache_data
def create_density_contour(df):
    """
    2D Density Contour for Recency vs Frequency
    """
    fig = px.density_heatmap(
        df, 
        x="Recency", 
        y="Frequency", 
        z="Monetary", 
        histfunc="sum",
        title="Shopping Trends Heatmap (Recency vs Frequency)",
        color_continuous_scale="Viridis"
    )
    return apply_theme(fig)

@st.cache_data
def create_pca_3d_plot(df):
    """
    3D PCA Scatter Plot to visualize high-dimensional clusters.
    """
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    
    # Select numeric features
    features = ["Recency", "Frequency", "Monetary", "LoyaltyScore", "AvgSessionTime"]
    x = df[features].dropna()
    
    # Standardize
    x = StandardScaler().fit_transform(x)
    
    # PCA
    pca = PCA(n_components=3)
    components = pca.fit_transform(x)
    
    total_var = pca.explained_variance_ratio_.sum() * 100
    
    # Create DF for plotting
    pca_df = pd.DataFrame(data=components, columns=['PC1', 'PC2', 'PC3'])
    pca_df['segment_name'] = df['segment_name'].values
    
    fig = px.scatter_3d(
        pca_df, 
        x='PC1', y='PC2', z='PC3', 
        color='segment_name',
        color_discrete_map=SEGMENT_COLORS,
        title=f"3D Cluster Visualization (PCA - {total_var:.1f}% Variance Explained)",
        opacity=0.7
    )
    
    fig.update_traces(marker=dict(size=5, line=dict(width=0)))
    fig.update_layout(scene = dict(
        xaxis_title='Principal Component 1',
        yaxis_title='Principal Component 2',
        zaxis_title='Principal Component 3',
        xaxis=dict(backgroundcolor='rgba(0,0,0,0)'),
        yaxis=dict(backgroundcolor='rgba(0,0,0,0)'),
        zaxis=dict(backgroundcolor='rgba(0,0,0,0)'),
    ))
    
    return apply_theme(fig)
    return apply_theme(fig)

@st.cache_data
def create_lollipop_chart(df, col, title, alias_key=None):
    """
    Lollipop Chart for Segment Distribution (Alternative to Bar/Donut)
    """
    counts = df[col].value_counts().reset_index()
    counts.columns = [col, 'count']
    
    # Alias mapping
    if alias_key:
        counts['label'] = counts[col].map(SEGMENT_ALIASES.get(alias_key, {}))
        counts['label'] = counts['label'].fillna(counts[col])
        color_map = {v: SEGMENT_COLORS.get(k, "#333") for k, v in SEGMENT_ALIASES.get(alias_key, {}).items()}
    else:
        counts['label'] = counts[col]
        color_map = SEGMENT_COLORS
        
    counts = counts.sort_values('count', ascending=True)

    fig = go.Figure()
    
    # Draw lines
    for i, row in counts.iterrows():
        color = color_map.get(row['label'], '#e0e0e0') if alias_key else SEGMENT_COLORS.get(row[col], '#e0e0e0')
        
        # The line
        fig.add_shape(
            type='line',
            x0=0, y0=i,
            x1=row['count'], y1=i,
            line=dict(color=color, width=3)
        )
        
        # The marker (Lollipop head)
        fig.add_trace(go.Scatter(
            x=[row['count']], 
            y=[i],
            mode='markers',
            marker=dict(color=color, size=18, line=dict(width=2, color='white')),
            name=row['label'],
            hoverinfo='text',
            hovertext=f"{row['label']}: {row['count']} Customers"
        ))

    fig.update_layout(
        title=title,
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(counts))),
            ticktext=counts['label'],
            showgrid=False
        ),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        showlegend=False,
        height=400
    )
    return apply_theme(fig)

@st.cache_data
def create_donut_chart(df, col, title, alias_key=None):
    """
    Donut Chart for distribution.
    """
    counts = df[col].value_counts().reset_index()
    counts.columns = [col, 'count']
    
    # Alias mapping
    if alias_key:
        counts['label'] = counts[col].map(SEGMENT_ALIASES.get(alias_key, {}))
        counts['label'] = counts['label'].fillna(counts[col])
        color_map = {v: SEGMENT_COLORS.get(k, "#333") for k, v in SEGMENT_ALIASES.get(alias_key, {}).items()}
        target_col = 'label'
    else:
        counts['label'] = counts[col]
        color_map = SEGMENT_COLORS
        target_col = col

    fig = px.pie(
        counts, 
        names='label', 
        values='count', 
        hole=0.4,
        title=title,
        color='label' if alias_key else col,
        color_discrete_map=color_map if alias_key else SEGMENT_COLORS
    )
    return apply_theme(fig)

@st.cache_data
def create_trend_chart(df):
    """
    Simulated Monthly Trend Chart (Line/Area)
    """
    # Simulate monthly data based on segment size
    months = pd.date_range(start='2024-01-01', periods=12, freq='M')
    data = []
    
    for segment in df['segment_name'].unique():
        base_val = len(df[df['segment_name'] == segment])
        # Random walk simulation
        trend = np.random.normal(loc=1.05, scale=0.1, size=12).cumprod() * base_val
        for i, m in enumerate(months):
            data.append({
                'Date': m,
                'Segment': segment,
                'Value': int(trend[i])
            })
            
    trend_df = pd.DataFrame(data)
    
    fig = px.area(
        trend_df,
        x="Date",
        y="Value",
        color="Segment",
        title="Projected Monthly Revenue Trend",
        color_discrete_map=SEGMENT_COLORS
    )
    return apply_theme(fig)

@st.cache_data
def create_stacked_bar(df):
    """
    Stacked Bar for Retention per Segment
    """
    # Group by Segment and Churn
    grouped = df.groupby(['segment_name', 'churn']).size().reset_index(name='count')
    grouped['Status'] = grouped['churn'].apply(lambda x: 'Churned' if x==1 else 'Retained')
    
    fig = px.bar(
        grouped,
        x="segment_name",
        y="count",
        color="Status",
        title="Retention Status by Segment",
        color_discrete_map={'Retained': '#00C853', 'Churned': '#D50000'},
        barmode='stack'
    )
    return apply_theme(fig)
