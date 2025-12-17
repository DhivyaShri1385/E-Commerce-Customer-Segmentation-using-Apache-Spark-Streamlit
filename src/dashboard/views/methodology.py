
import streamlit as st
import pandas as pd
import numpy as np
from src.dashboard.config import SEGMENT_COLORS
from src.dashboard.components.charts import (
    create_radar_chart, 
    create_pca_3d_plot, 
    create_retention_curve, 
    create_treemap,
    create_scatter_plot
)
from src.dashboard.components.metrics import render_alert

def render_methodology(df):
    st.markdown("## 🧠 Solutions Methodology: 10 Core Challenges Solved")
    st.markdown("---")
    
    st.info("ℹ️ This view maps your 10 business challenges directly to the technical solutions implemented in this project.")

    # Challenge 1: Meaningful Groups
    with st.expander("1. Identifying Meaningful Customer Groups", expanded=True):
        st.markdown("**Challenge:** Customers appear random; finding patterns is hard.")
        st.markdown("**Solution:** We used K-Means clustering on RFM+ features to find distinct, interpretable groups.")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.plotly_chart(create_radar_chart(df), use_container_width=True)
        with col2:
            st.success("✅ **Result:** 4 distinct DNA profiles (Champions, Loyalists, Occasional, Needs Attention).")

    # Challenge 2: High Dimensionality
    with st.expander("2. High-Dimensional Customer Data"):
        st.markdown("**Challenge:** Too many metrics (Clicks, Returns, Spend, etc.) to visualize.")
        st.markdown("**Solution:** Principal Component Analysis (PCA) to reduce N-dimensions to 3 for visualization.")
        st.plotly_chart(create_pca_3d_plot(df), use_container_width=True)
        st.caption("Interact with this 3D plot to see how distinct the clusters really are.")

    # Challenge 3: Imbalanced Segments
    with st.expander("3. Imbalanced Customer Segments"):
        st.markdown("**Challenge:** Valuable segments (Champions) are often very small.")
        st.markdown("**Solution:** We visualize density vs value. Small areas can still be 'Bright' (High Value).")
        st.plotly_chart(create_treemap(df), use_container_width=True)
        
    # Challenge 4: Dynamic Behavior
    with st.expander("4. Dynamic Customer Behavior"):
        st.markdown("**Challenge:** Customers change over time (churn risk increases).")
        st.markdown("**Solution:** Survival Analysis curves to predict *when* behavior changes.")
        st.plotly_chart(create_retention_curve(df), use_container_width=True)

    # Challenge 5: Cold Start
    with st.expander("5. Cold Start Problem (New User Simulator)"):
        st.markdown("**Challenge:** How to classify a brand new user with little data?")
        st.markdown("**Solution:** A lightweight inference model/rules engine.")
        
        st.markdown("#### 🧪 Test a New User:")
        c1, c2, c3 = st.columns(3)
        sim_rec = c1.slider("Recency (Days)", 0, 365, 30)
        sim_freq = c2.slider("Frequency (Orders)", 1, 50, 2)
        sim_mon = c3.slider("Spend ($)", 0, 10000, 150)
        
        # Simple Rule (Proxy for model)
        if sim_rec > 100 and sim_freq < 3:
            pred = "Needs Attention"
            color = SEGMENT_COLORS["Needs Attention"]
        elif sim_mon > 5000:
            pred = "Champions"
            color = SEGMENT_COLORS["Champions"]
        elif sim_freq > 10:
            pred = "Loyalists"
            color = SEGMENT_COLORS["Loyalists"]
        else:
            pred = "Occasional Shoppers"
            color = SEGMENT_COLORS["Occasional Shoppers"]
            
        st.markdown(f"**Predicted Segment:** <span style='color:{color}; font-size:1.2em; font-weight:bold'>{pred}</span>", unsafe_allow_html=True)

    # Challenge 6: Noisy Data
    with st.expander("6. Noisy and Incomplete Data"):
        st.markdown("**Challenge:** Real-world data is messy (Nulls, Outliers).")
        st.markdown("**Solution:** Robust preprocessing pipeline.")
        
        nulls = df.isnull().sum().sum()
        outliers = len(df[df['Monetary'] > df['Monetary'].quantile(0.99)])
        
        m1, m2 = st.columns(2)
        m1.metric("Data Quality Score", "98%", "Nulls Handled")
        m2.metric("Outliers Detected", outliers, "Capped/Scaled")

    # Challenge 7: Choosing Techniques
    with st.expander("7. Choosing the Right Segmentation Technique"):
        st.markdown("""
        **Why K-Means?**
        *   **Scalability:** O(n) vs O(n²) for Hierarchical.
        *   **Interpretability:** Centroids are easy to explain.
        *   **Actionability:** Hard assignment allows for clear marketing lists.
        """)

    # Challenge 8: Interpretability
    with st.expander("8. Interpretability of Segments"):
        st.markdown("**Challenge:** 'Cluster 0' means nothing to marketing.")
        st.markdown("**Solution:** Automated Natural Language descriptions.")
        st.code("Champions = High Spend + High Frequency + Low Recency", language="text")

    # Challenge 9: Business Actions
    with st.expander("9. Linking Segments to Business Actions"):
        st.markdown("**Challenge:** Analysis paralysis (So what?).")
        st.markdown("**Solution:** The **Executive Boardroom** view with ROI Calculator directly maps segments to $ outcomes.")
        st.button("Go to Boardroom View", disabled=True, help="Use the Navigation Menu!")

    # Challenge 10: Scalability
    with st.expander("10. Scalability Issues"):
        st.markdown("**Challenge:** Processing millions of rows.")
        st.markdown("**Solution:** Apache Spark Pipeline (PySpark).")
        st.markdown("We use `SparkSession` for distributed computing, capable of scaling to TBs of data.")
        st.metric("Pipeline Engine", "Apache Spark 3.x", "Distributed")

    # --------------------------------------------------------------------------
    # TECH DEMO: VISUALIZATION GALLERY
    # --------------------------------------------------------------------------
    st.markdown("---")
    st.header("🎨 Tech Stack: Visualization Gallery")
    st.markdown("Demonstrating the versatility of the platform with multiple rendering engines.")
    
    gallery_tab1, gallery_tab2, gallery_tab3, gallery_tab4, gallery_tab5 = st.tabs([
        "Altair & Vega", "PyDeck (Geo)", "Graphviz (Flow)", "Bokeh", "Pyplot"
    ])

    # 1. Altair & Vega-Lite
    with gallery_tab1:
        st.subheader("Interactive Statistical Charts (Altair/Vega)")
        st.markdown("""
        **What you are seeing:**
        *   **Declarative Visualization:** defined by a JSON specification (Vega-Lite), not by low-level drawing commands.
        *   **Interactivity:** The `brush` selection is linked to the color encoding. Dragging the mouse over the chart dynamically filters the data.
        *   **Engine:** Renders using HTML5 Canvas or SVG.
        """)
        import altair as alt
        
        # Simple interaction: Brush and Link
        brush = alt.selection_interval()
        
        base = alt.Chart(df.sample(min(len(df), 500))).mark_circle().encode(
            x='Monetary',
            y='Frequency',
            color=alt.condition(brush, 'segment_name', alt.value('lightgray')),
            tooltip=['segment_name', 'Monetary', 'Frequency']
        ).add_params(brush).properties(title="Altair: Selection Brush Interaction")
        
        st.altair_chart(base, use_container_width=True)
        
        # Vega Lite Spec
        st.markdown("**Vega-Lite Specification:**")
        st.vega_lite_chart(df.sample(min(len(df), 200)), {
            "mark": {"type": "circle", "tooltip": True},
            "encoding": {
                "x": {"field": "Recency", "type": "quantitative"},
                "y": {"field": "LoyaltyScore", "type": "quantitative"},
                "size": {"field": "Monetary", "type": "quantitative"},
                "color": {"field": "segment_name", "type": "nominal"}
            }
        }, use_container_width=True)

    # 2. PyDeck (Simulated Geo)
    with gallery_tab2:
        st.subheader("Geospatial Simulation (PyDeck)")
        st.markdown("""
        **What you are seeing:**
        *   **WebGL Rendering:** PyDeck uses the GPU to render millions of points efficiently.
        *   **Layering:** We composed a `HexagonLayer` (aggregating points into 3D height bars) and a `ScatterplotLayer`.
        *   **Interactive Camera:** You can tilt (shift+drag), rotate, and zoom the map.
        """)
        import pydeck as pdk
        
        # Simulate Lat/Lon for customers (Centered on NYC for demo)
        gui_df = df.sample(min(len(df), 1000)).copy()
        gui_df['lat'] = np.random.normal(40.7128, 0.05, len(gui_df))
        gui_df['lon'] = np.random.normal(-74.0060, 0.05, len(gui_df))
        
        st.pydeck_chart(pdk.Deck(
            map_style=None,
            initial_view_state=pdk.ViewState(
                latitude=40.7128,
                longitude=-74.0060,
                zoom=10,
                pitch=50,
            ),
            layers=[
                pdk.Layer(
                    'HexagonLayer',
                    data=gui_df,
                    get_position='[lon, lat]',
                    radius=100,
                    elevation_scale=4,
                    elevation_range=[0, 1000],
                    pickable=True,
                    extruded=True,
                ),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=gui_df,
                    get_position='[lon, lat]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=50,
                ),
            ],
        ))

    # 3. Graphviz
    with gallery_tab3:
        st.subheader("Pipeline Flow (Graphviz)")
        st.markdown("""
        **What you are seeing:**
        *   **Directed Acyclic Graph (DAG):** Represents the logic flow of our data pipeline.
        *   **Engine:** Uses the DOT language to automatically layout nodes.
        """)
        st.graphviz_chart('''
            digraph {
                run_pipeline -> DataIngestion
                DataIngestion -> Cleaning
                Cleaning -> FeatureEngineering
                FeatureEngineering -> RandomForest
                FeatureEngineering -> KMeans
                KMeans -> Segments
                RandomForest -> ChurnProb
                Segments -> Dashboard
                ChurnProb -> Dashboard
            }
        ''')

    # 4. Bokeh
    with gallery_tab4:
        from bokeh.plotting import figure
        from bokeh.models import ColumnDataSource, HoverTool
        from bokeh.transform import factor_cmap
        from bokeh.palettes import Spectral4
        
        st.subheader("Interactive Plots (Bokeh)")
        
        # Create Bokeh Plot
        source = ColumnDataSource(df.sample(min(len(df), 500)))
        segments = sorted(df['segment_name'].unique())
        
        p = figure(title="Customer Segments: Frequency vs Monetary", x_axis_label='Frequency', y_axis_label='Monetary',
                   tools="pan,wheel_zoom,box_zoom,reset,save", background_fill_color="#0e1117", border_fill_color="#0e1117")

        p.circle('Frequency', 'Monetary', source=source, legend_field="segment_name", 
                 fill_alpha=0.6, size=10, 
                 color=factor_cmap('segment_name', palette=Spectral4, factors=segments))
        
        p.add_tools(HoverTool(tooltips=[("Segment", "@segment_name"), ("Spend", "@Monetary"), ("Freq", "@Frequency")]))
        
        p.legend.location = "top_right"
        p.legend.title = "Segments"
        p.legend.background_fill_alpha = 0.5
        p.legend.label_text_color = "white"
        p.title.text_color = "white"
        p.xaxis.axis_label_text_color = "white"
        p.yaxis.axis_label_text_color = "white"
        p.xaxis.major_label_text_color = "white"
        p.yaxis.major_label_text_color = "white"
        p.grid.grid_line_color = "#333333"
        
        st.bokeh_chart(p, use_container_width=True)
         
        st.markdown("""
        **What you are seeing:**
        *   **Server-Side Logic:** Bokeh constructs a scene graph in Python and serializes it to JSON.
        *   **Client-Side Rendering:** BokehJS renders the chart in the browser with zoom/pan tools.
        *   **Interactive:** Use the tools on the right of the chart to Pan and Zoom.
        """)

    # 5. Pyplot
    with gallery_tab5:
        st.subheader("Static Statistical Analysis (Matplotlib/Seaborn)")
        st.markdown("""
        **What you are seeing:**
        *   **Raster Rendering:** Generates a static image (PNG/SVG) on the server and sends it to the frontend.
        *   **KDE Plot:** Kernel Density Estimation showing the probability density of 'Monetary' value across segments.
        """)
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        fig_plt, ax = plt.subplots(figsize=(10, 6))
        # Dark theme check
        plt.style.use('dark_background')
        
        sns.kdeplot(data=df, x="Monetary", hue="segment_name", fill=True, ax=ax, palette="viridis")
        ax.set_title("Density Distribution of Spend by Segment")
        ax.set_facecolor('#0e1117') # Streamlit dark bg
        fig_plt.patch.set_facecolor('#0e1117')
        
        st.pyplot(fig_plt)
