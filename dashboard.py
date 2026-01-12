"""
Dashboard Module
Displays analytics and history from database
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import DatabaseManager

def display_dashboard():
    """Display main dashboard with analytics"""
    
    st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
    
    st.title("📊 Resume-JD Matcher Dashboard")
    st.markdown("Analytics and matching history")
    
    db = DatabaseManager()
    
    # Get statistics
    stats = db.get_dashboard_stats()
    
    st.divider()
    
    # Summary Metrics
    st.subheader("📈 Overall Statistics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Single Matches",
            stats['single_matches']['total'],
            delta=None
        )
    
    with col2:
        st.metric(
            "Single Avg Score",
            f"{stats['single_matches']['average_score']}/100",
            delta=None
        )
    
    with col3:
        st.metric(
            "Single Top Score",
            f"{stats['single_matches']['highest_score']}/100",
            delta=None
        )
    
    with col4:
        st.metric(
            "Batch Processes",
            stats['batch_results']['total'],
            delta=None
        )
    
    with col5:
        st.metric(
            "Total Candidates",
            stats['total_candidates'],
            delta=None
        )
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Analytics",
        "📜 Single Match History",
        "📂 Batch History",
        "⚙️ Database Management"
    ])
    
    # ==================== ANALYTICS TAB ====================
    with tab1:
        st.subheader("Analytics Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Score distribution
            single_matches = db.get_all_single_matches(limit=1000)
            
            if single_matches:
                scores = [m['overall_score'] for m in single_matches]
                
                fig = px.histogram(
                    x=scores,
                    nbins=10,
                    title="Single Match Score Distribution",
                    labels={'x': 'Score', 'y': 'Frequency'},
                    color_discrete_sequence=['#4ECDC4']
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No single match data available")
        
        with col2:
            # Assessment breakdown pie chart
            if single_matches:
                assessment_data = {}
                for match in single_matches:
                    assessment = match['assessment']
                    assessment_data[assessment] = assessment_data.get(assessment, 0) + 1
                
                fig = px.pie(
                    values=list(assessment_data.values()),
                    names=list(assessment_data.keys()),
                    title="Assessment Distribution",
                    color_discrete_map={
                        'Excellent Match': '#2ecc71',
                        'Good Match': '#f39c12',
                        'Needs Review': '#e74c3c'
                    }
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No assessment data available")
        
        st.divider()
        
        # Batch statistics
        st.subheader("Batch Processing Analytics")
        
        batch_results = db.get_all_batch_results(limit=50)
        
        if batch_results:
            batch_df = pd.DataFrame(batch_results)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Batch scores over time
                batch_df['created_at'] = pd.to_datetime(batch_df['created_at'])
                
                fig = px.line(
                    batch_df,
                    x='created_at',
                    y='average_score',
                    title='Batch Average Score Over Time',
                    labels={'created_at': 'Date', 'average_score': 'Average Score'},
                    color_discrete_sequence=['#3498db']
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Batch size comparison
                fig = px.bar(
                    batch_df,
                    x='batch_id',
                    y='total_resumes',
                    title='Resumes Per Batch',
                    labels={'batch_id': 'Batch ID', 'total_resumes': 'Count'},
                    color_discrete_sequence=['#9b59b6']
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No batch processing data available")
    
    # ==================== SINGLE MATCH HISTORY TAB ====================
    with tab2:
        st.subheader("Single Match History")
        
        single_matches = db.get_all_single_matches(limit=100)
        
        if single_matches:
            # Convert to DataFrame
            df = pd.DataFrame(single_matches)
            df = df[['id', 'resume_name', 'job_title', 'overall_score', 'assessment', 'created_at']]
            df = df.sort_values('created_at', ascending=False)
            
            # Display table
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # Export options
            st.subheader("📥 Export Data")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # CSV export
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    "single_matches.csv",
                    "text/csv"
                )
            
            with col2:
                # JSON export
                json_str = df.to_json(orient='records', indent=2)
                st.download_button(
                    "📄 Download JSON",
                    json_str,
                    "single_matches.json",
                    "application/json"
                )
            
            with col3:
                st.info("Exports selected columns only")
            
            st.divider()
            
            # Delete old records
            st.subheader("🗑️ Clean Up")
            
            days = st.slider("Delete records older than (days):", 1, 365, 90)
            
            if st.button("🗑️ Delete Old Records"):
                db.clear_old_data(days)
                st.success(f"✅ Records older than {days} days deleted")
                st.rerun()
        
        else:
            st.info("No single match history available")
    
    # ==================== BATCH HISTORY TAB ====================
    with tab3:
        st.subheader("Batch Processing History")
        
        batch_results = db.get_all_batch_results(limit=100)
        
        if batch_results:
            # Convert to DataFrame
            df = pd.DataFrame(batch_results)
            df = df[['batch_id', 'job_title', 'total_resumes', 'average_score', 'highest_score', 'created_at']]
            df = df.sort_values('created_at', ascending=False)
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # View batch details
            st.subheader("📋 View Batch Details")
            
            selected_batch = st.selectbox(
                "Select batch to view:",
                [f"{b['batch_id']} - {b['job_title']}" for b in batch_results]
            )
            
            if selected_batch:
                batch_id = selected_batch.split(' - ')[0]
                batch_data = db.get_batch_result(batch_id)
                
                if batch_data:
                    st.write(f"**Batch ID**: {batch_data['batch_id']}")
                    st.write(f"**Job Title**: {batch_data['job_title']}")
                    st.write(f"**Total Resumes**: {batch_data['total_resumes']}")
                    st.write(f"**Average Score**: {batch_data['average_score']:.1f}")
                    
                    st.divider()
                    
                    # Show candidates
                    st.subheader("📊 Candidates in Batch")
                    
                    candidates_data = []
                    for candidate in batch_data['candidates']:
                        candidates_data.append({
                            'Rank': candidate['rank'],
                            'Resume': candidate['resume_name'],
                            'Score': candidate['overall_score'],
                            'Assessment': candidate['assessment'],
                            'Experience': '✅' if candidate['experience_met'] else '❌',
                            'Education': '✅' if candidate['education_met'] else '❌',
                            'Skills': f"{candidate['skills_percentage']}%"
                        })
                    
                    candidates_df = pd.DataFrame(candidates_data)
                    st.dataframe(candidates_df, use_container_width=True, hide_index=True)
        
        else:
            st.info("No batch processing history available")
    
    # ==================== DATABASE MANAGEMENT TAB ====================
    with tab4:
        st.subheader("⚙️ Database Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Database Size", f"{db.get_database_size()} MB")
        
        with col2:
            st.metric("Database Location", str(db.db_path))
        
        with col3:
            st.info("data.db")
        
        st.divider()
        
        # Database operations
        st.subheader("Operations")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Analytics"):
                db.update_analytics()
                st.success("✅ Analytics updated")
                st.rerun()
        
        with col2:
            if st.button("💾 Backup Database"):
                if db.backup_database():
                    st.success("✅ Database backed up")
                else:
                    st.error("❌ Backup failed")
        
        with col3:
            if st.button("🔍 Vacuum Database"):
                try:
                    conn = db.get_connection()
                    conn.execute('VACUUM')
                    conn.close()
                    st.success("✅ Database optimized")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        st.divider()
        
        # Danger zone
        st.subheader("🚨 Danger Zone")
        
        st.warning("⚠️ These actions cannot be undone!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear All Single Matches"):
                try:
                    conn = db.get_connection()
                    conn.execute('DELETE FROM single_matches')
                    conn.commit()
                    conn.close()
                    st.success("✅ All single matches deleted")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        with col2:
            if st.button("🗑️ Clear All Batch Results"):
                try:
                    conn = db.get_connection()
                    conn.execute('DELETE FROM batch_candidates')
                    conn.execute('DELETE FROM batch_results')
                    conn.commit()
                    conn.close()
                    st.success("✅ All batch results deleted")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")

if __name__ == "__main__":
    display_dashboard()