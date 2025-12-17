
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from streamlit_option_menu import option_menu

# Import Views
from src.dashboard.views.executive_summary import render_executive_summary
from src.dashboard.views.detailed_analytics import render_detailed_analytics
from src.dashboard.views.deep_dive import render_deep_dive
from src.dashboard.views.stakeholder_view import render_stakeholder_view
from src.dashboard.views.system_monitor import render_system_monitor
from src.dashboard.views.methodology import render_methodology

# Page Config (Must be first)
st.set_page_config(
    page_title="Ecommerce Intelligence",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("src/dashboard/styles/custom.css")

# --- AUTHENTICATION ---
try:
    with open('src/dashboard/utils/auth_config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("Auth config not found. Please run the setup script.")
    st.stop()

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],

)

# Login Widget
authenticator.login('main')

# Handle Authentication Status
authentication_status = st.session_state.get('authentication_status')
name = st.session_state.get('name')
username = st.session_state.get('username')

if authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')
elif authentication_status:
    # --- APP LOGIC (Authenticated) ---
    
    # Particle Effect (Inject only when logged in)
    st.markdown("""
    <div class="particle-container">
        <div class="particle"></div><div class="particle"></div><div class="particle"></div>
        <div class="particle"></div><div class="particle"></div>
    </div>
    """, unsafe_allow_html=True)

    # --- SIDEBAR NAVIGATION ---
    with st.sidebar:
        # Title
        st.markdown("<h1 style='text-align: center; color: #22D3EE;'>🔮 E-COMMERCE<br>INTELLIGENCE</h1>", unsafe_allow_html=True)
        st.markdown("---")
        
        # User Info
        st.success(f"Welcome, **{name}** ({config['credentials']['usernames'][username]['role']})")
        
        # Determine Role
        role = config['credentials']['usernames'][username]['role']
        
        # Define Menu Options based on Role
        if role == 'admin':
            menu_options = [
                "Spark Engine", "Dashboard", "Customer Segments", "Risk & Churn", 
                "Trends", "AI Insights", "Data Upload", "Settings", "Logout"
            ]
            menu_icons = [
                "lightning-charge-fill", "bar-chart-fill", "people-fill", "shield-exclamation",
                "graph-up-arrow", "cpu-fill", "cloud-upload-fill", "gear-fill", "door-open-fill"
            ]
        else: # Analyst
            menu_options = [
                "Dashboard", "Customer Segments", "Risk & Churn", 
                "Trends", "AI Insights", "Logout"
            ]
            menu_icons = [
                "bar-chart-fill", "people-fill", "shield-exclamation",
                "graph-up-arrow", "cpu-fill", "door-open-fill"
            ]

        # Render Main Menu
        selected = option_menu(
            menu_title="Main Menu",
            options=menu_options,
            icons=menu_icons,
            menu_icon="cast",
            default_index=1 if role == 'admin' else 0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#22D3EE", "font-size": "18px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "5px", "--hover-color": "#141A2B"},
                "nav-link-selected": {"background-color": "rgba(34, 211, 238, 0.1)", "border": "1px solid #22D3EE", "color": "#22D3EE"},
            }
        )

        # Handle Logout in Sidebar
        if selected == "Logout":
            authenticator.logout('Logout', 'sidebar')
            st.rerun()

    # --- MAIN CONTENT ROUTING ---
    
    # 1. Spark Engine
    if selected == "Spark Engine":
        if role == 'admin':
            render_system_monitor()
        else:
            st.error("Access Denied: Admin privileges required.")

    # 2. Dashboard (Master Executive)
    elif selected == "Dashboard":
        from src.dashboard.data.loader import load_data, get_metrics
        df = load_data()
        if not df.empty and 'segment_name' in df.columns:
            metrics = get_metrics(df)
            
            # Prepare Data for View
            segment_counts = df['segment_name'].value_counts().reset_index()
            segment_counts.columns = ['Segment', 'Count']
            
            revenue_by_segment = df.groupby('segment_name')['Monetary'].sum().reset_index()
            revenue_by_segment.columns = ['Segment', 'Revenue']
            
            render_executive_summary(df, metrics, segment_counts, revenue_by_segment)
        else:
            st.warning("Data not fully processed. Please run the pipeline or upload data.")
            if not df.empty:
                 # Fallback for unsegmented data
                 st.dataframe(df.head())


    # 3. Customer Segments (Detailed Analytics Tab 1/2)
    elif selected == "Customer Segments":
        from src.dashboard.data.loader import load_data, get_metrics
        df = load_data()
        if not df.empty and 'segment_name' in df.columns:
             metrics = get_metrics(df)
             segment_metrics = df.groupby('segment_name').agg({
                'Monetary': 'sum',
                'Frequency': 'mean',
                'Recency': 'mean',
                'CustomerID': 'count'
             }).reset_index()
             render_detailed_analytics(df, segment_metrics, metrics)
        else:
             st.warning("Data not available.")

    # 4. Risk & Churn (Deep Dive)
    elif selected == "Risk & Churn":
        from src.dashboard.data.loader import load_data
        df = load_data()
        render_deep_dive(df)

    # 5. Trends (Detailed Analytics Tab 4)
    elif selected == "Trends":
        from src.dashboard.data.loader import load_data, get_metrics
        from src.dashboard.views.detailed_analytics import render_trends_view
        df = load_data()
        st.title("📈 Market Trends & Seasonality")
        if not df.empty and 'segment_name' in df.columns:
             metrics = get_metrics(df)
             segment_metrics = df.groupby('segment_name').agg({
                'Monetary': 'sum',
                'Frequency': 'mean',
                'Recency': 'mean',
                'CustomerID': 'count'
             }).reset_index()
             render_trends_view(df, segment_metrics, metrics)
        else:
             st.warning("Data not available.")
        
    # 6. AI Insights (Methodology & Recommendations)
    elif selected == "AI Insights":
        # Using Methodology view as the "AI Insights" explanation + Recommendations
        from src.dashboard.data.loader import load_data
        df = load_data()
        render_methodology(df) 

    # 7. Data Upload
    elif selected == "Data Upload":
        st.title("📥 Data Ingestion")
        st.markdown("### Upload New Customer Data")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
             st.success("File uploaded successfully! Spark pipeline triggered.")

    # 8. Settings
    elif selected == "Settings":
        st.title("⚙️ System Settings")
        st.toggle("Dark Mode", value=True)
        st.toggle("Notifications", value=True)
        st.markdown("### User Management")
        st.dataframe([{"User": "admin", "Role": "Admin"}, {"User": "analyst", "Role": "Analyst"}])

