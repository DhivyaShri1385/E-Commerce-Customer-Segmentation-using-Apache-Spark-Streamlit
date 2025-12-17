
import streamlit as st

def render_metric_section(title, description, icon, content_func):
    """
    Renders a unified metric section box.
    content_func: a function that renders the content inside (charts, metrics, etc.)
    """
    st.markdown('<div class="metric-section">', unsafe_allow_html=True)
    st.markdown('<div class="metric-header">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-icon-large">{icon}</div>', unsafe_allow_html=True)
    st.markdown(f'''
    <div>
        <h2 class="metric-title">{title}</h2>
        <p class="metric-description">{description}</p>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    content_func()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_metric_card(value, label, sublabel=""):
    st.markdown(f'''
    <div class="insight-card">
        <div class="insight-value">{value}</div>
        <div class="insight-label">{label}</div>
        {f'<div class="insight-sublabel">{sublabel}</div>' if sublabel else ''}
    </div>
    ''', unsafe_allow_html=True)

def render_progress_bar(percentage, label):
    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
    st.markdown('<div class="progress-bar">', unsafe_allow_html=True)
    st.markdown(f'<div class="progress-fill" style="width: {min(100, percentage)}%;"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="progress-text">{label}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_alert(type, title, subtitle1, subtitle2):
    """
    type: 'alert-high', 'warning-panel', 'success-panel', 'business-value', 'info-panel'
    """
    st.markdown(f'''
    <div class="{type}">
        {title}<br>
        <small>{subtitle1}</small><br>
        <small>{subtitle2}</small>
    </div>
    ''', unsafe_allow_html=True)
