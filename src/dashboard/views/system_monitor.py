
import streamlit as st
import streamlit.components.v1 as components
import requests


import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def get_spark_metrics(base_url="http://localhost:4040"):
    try:
        # 1. Get Application ID
        apps_resp = requests.get(f"{base_url}/api/v1/applications", timeout=0.5)
        if apps_resp.status_code != 200 or not apps_resp.json():
            return None
        
        app_id = apps_resp.json()[0]['id']
        app_name = apps_resp.json()[0]['name']
        
        # 2. Get Jobs
        jobs_resp = requests.get(f"{base_url}/api/v1/applications/{app_id}/jobs", timeout=0.5)
        jobs_data = jobs_resp.json() if jobs_resp.status_code == 200 else []
        
        # 3. Get Executors (Resource Usage)
        exec_resp = requests.get(f"{base_url}/api/v1/applications/{app_id}/executors", timeout=0.5)
        exec_data = exec_resp.json() if exec_resp.status_code == 200 else []
        
        return {
            "app_id": app_id,
            "app_name": app_name,
            "jobs": jobs_data,
            "executors": exec_data
        }
    except Exception as e:
        return None

def render_system_monitor():
    st.markdown("## 🖥️ System Monitor & Pipeline Status")
    st.markdown("---")

    # --- SECURITY GATE ---
    if 'spark_unlocked' not in st.session_state:
        st.session_state['spark_unlocked'] = False
        
    if not st.session_state['spark_unlocked']:
        st.warning("🔒 Restrictive Access Area")
        st.markdown("Please enter the Spark Administrator Password to access the system monitor.")
        password = st.text_input("Spark Admin Password", type="password")
        
        if st.button("Unlock Spark UI"):
            if password == "spark-admin":
                st.session_state['spark_unlocked'] = True
                st.success("Access Granted.")
                st.rerun()
            else:
                st.error("Incorrect Password.")
        return # Stop rendering if locked

    # --- UNLOCKED CONTENT ---
    metrics = get_spark_metrics()
    
    if metrics:
        st.success(f"✅ Connected to Spark App: **{metrics['app_name']}** (`{metrics['app_id']}`)")
        st.markdown("🌐 **Native UI:** [http://localhost:4040](http://localhost:4040)")
        
        # KEY METRICS ROW
        col1, col2, col3, col4 = st.columns(4)
        
        df_jobs = pd.DataFrame(metrics['jobs'])
        if not df_jobs.empty:
            active_jobs = len(df_jobs[df_jobs['status'] == 'RUNNING'])
            completed_jobs = len(df_jobs[df_jobs['status'] == 'SUCCEEDED'])
            failed_jobs = len(df_jobs[df_jobs['status'] == 'FAILED'])
            
            with col1:
                render_metric_card("Active Jobs", active_jobs, "⚡")
            with col2:
                render_metric_card("Completed", completed_jobs, "✅")
            with col3:
                render_metric_card("Failed", failed_jobs, "❌", is_risk=True if failed_jobs > 0 else False)
        else:
             st.info("No jobs found yet.")

        # Executor Stats
        df_exec = pd.DataFrame(metrics['executors'])
        if not df_exec.empty and 'memoryUsed' in df_exec.columns:
            total_mem = df_exec['memoryUsed'].sum() / (1024 * 1024) # MB
            with col4:
                render_metric_card("Mem Used", f"{total_mem:.1f} MB", "💾")
        
        st.markdown("---")

        tab1, tab2, tab3 = st.tabs(["📈 Performance Graphs", "🕸️ Job Timeline", "💻 Resource Monitor"])
        
        # TAB 1: PERF GRAPHS (Tasks & Stages)
        with tab1:
            st.markdown("### Job Duration & Complexity")
            if not df_jobs.empty:
                # Duration Chart
                # Parse strings to timestamps if needed, usually Spark returns ISO strings
                if 'submissionTime' in df_jobs.columns and 'completionTime' in df_jobs.columns:
                     try:
                        df_jobs['start'] = pd.to_datetime(df_jobs['submissionTime'])
                        df_jobs['end'] = pd.to_datetime(df_jobs['completionTime'])
                        df_jobs['duration_s'] = (df_jobs['end'] - df_jobs['start']).dt.total_seconds()
                        
                        fig_dur = px.bar(
                            df_jobs, x='jobId', y='duration_s', 
                            color='status', title="Job Duration (seconds)",
                            color_discrete_map={'SUCCEEDED': '#4ecdc4', 'FAILED': '#ff6b6b', 'RUNNING': '#ffd93d'}
                        )
                        st.plotly_chart(fig_dur, use_container_width=True)
                     except Exception as e:
                         st.warning(f"Could not parse dates: {e}")

        # TAB 2: TIMELINE
        with tab2:
             if not df_jobs.empty and 'start' in df_jobs.columns:
                 fig_gantt = px.timeline(
                     df_jobs, x_start="start", x_end="end", y="jobId", color="status",
                     title="Execution Timeline", labels={"jobId": "Job ID"}
                 )
                 fig_gantt.update_yaxes(autorange="reversed")
                 st.plotly_chart(fig_gantt, use_container_width=True)
             else:
                 st.info("Waiting for jobs to complete to generate timeline...")

        # TAB 3: RESOURCES (Original Iframe fallback + Executor info)
        with tab3:
            st.markdown("### Executor Details")
            if not df_exec.empty:
                # Select available columns only
                potential_cols = ['id', 'hostPort', 'isActive', 'totalTasks', 'failedTasks', 'completedTasks', 'totalInputBytes', 'totalShuffleRead']
                cols_to_show = [c for c in potential_cols if c in df_exec.columns]
                
                display_df = df_exec[cols_to_show].copy()
                if 'isActive' in display_df.columns:
                    display_df['State'] = display_df['isActive'].apply(lambda x: "🟢 Active" if x else "🔴 Dead")
                    # Move State to front if possible
                    cols = ['id', 'State'] + [c for c in display_df.columns if c not in ['id', 'State', 'isActive']]
                    display_df = display_df[cols]
                
                st.dataframe(display_df, use_container_width=True)
            
            st.markdown("### Native Spark UI")
            components.iframe("http://localhost:4040", height=600, scrolling=True)

    else:
        st.error("❌ Spark UI is unreachable.")
        st.warning("Ensure the pipeline is running with `python -m src.pipeline.run_pipeline --keep-alive`")

def render_metric_card(title, value, icon, is_risk=False):
    color = "#ff6b6b" if is_risk else "#22D3EE"
    bg_color = "rgba(255, 107, 107, 0.1)" if is_risk else "rgba(34, 211, 238, 0.1)"
    st.markdown(f"""
    <div style="background-color: {bg_color}; border: 1px solid {color}; padding: 15px; border-radius: 10px; text-align: center;">
        <div style="font-size: 2em;">{icon}</div>
        <div style="color: #bbb; font-size: 0.9em;">{title}</div>
        <div style="color: {color}; font-size: 1.5em; font-weight: bold;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

