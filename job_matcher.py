import streamlit as st
import pandas as pd
import job_scraper
import user_skills
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def render_job_matcher_ui():
    """Render the Job Matcher UI in the Streamlit app"""
    st.header("Career Matcher")
    
    # User login/registration section
    user_section, skills_section = st.columns([1, 1])
    
    with user_section:
        st.subheader("User Profile")
        
        if st.session_state.user_id is None:
            with st.form("user_login_form"):
                st.write("Please log in or register to use the Job Matcher")
                email = st.text_input("Email")
                name = st.text_input("Name")
                
                submitted = st.form_submit_button("Login / Register")
                if submitted and email:
                    # Try to get existing user
                    user_info = user_skills.get_user_by_email(email)
                    
                    if user_info:
                        # Existing user
                        st.session_state.user_id = user_info["id"]
                        st.session_state.user_email = email
                        if "skills" in user_info:
                            st.session_state.user_skills = user_info["skills"]
                        st.success(f"Welcome back, {user_info['name']}!")
                    else:
                        # New user
                        if name:
                            user_id = user_skills.create_user(name, email, [])
                            st.session_state.user_id = user_id
                            st.session_state.user_email = email
                            st.session_state.user_skills = []
                            st.success(f"Welcome, {name}! Your account has been created.")
                        else:
                            st.error("Name is required for new users.")
        else:
            # Display logged in user info
            user_info = user_skills.get_user_by_id(st.session_state.user_id)
            if user_info:
                st.write(f"**Logged in as:** {user_info['name']} ({user_info['email']})")
                
                if st.button("Log Out"):
                    st.session_state.user_id = None
                    st.session_state.user_email = None
                    st.session_state.user_skills = []
                    st.session_state.job_results = []
                    st.rerun()
    
    # Skills section
    with skills_section:
        st.subheader("Your Skills")
        
        if st.session_state.user_id:
            # Get current skills
            current_skills = st.session_state.user_skills
            
            # Skills input
            skill_input = st.text_area(
                "Enter your skills (comma separated)",
                value=", ".join(current_skills) if current_skills else "", 
                help="Example: Python, SQL, Data Analysis, Machine Learning"
            )
            
            if st.button("Update Skills"):
                # Parse skills
                skills_list = [skill.strip() for skill in skill_input.split(',') if skill.strip()]
                
                # Update user skills
                if user_skills.update_user_skills(st.session_state.user_id, skills_list):
                    st.session_state.user_skills = skills_list
                    st.success("Skills updated successfully!")
                else:
                    st.error("Failed to update skills. Please try again.")
    
    # Job search section
    if st.session_state.user_id:
        st.subheader("Find Matching Jobs")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Job search form
            with st.form("job_search_form"):
                skills_str = ", ".join(st.session_state.user_skills) if st.session_state.user_skills else ""
                search_skills = st.text_input("Skills to search for", value=skills_str)
                location = st.text_input("Location (leave empty for remote options)", value="")
                
                min_match = st.slider("Minimum skill match percentage", 0, 100, 50)
                
                submitted = st.form_submit_button("Find Jobs")
                if submitted:
                    if not search_skills.strip():
                        st.error("Please enter at least one skill to search for.")
                    else:
                        with st.spinner("Searching for jobs..."):
                            # Search for jobs
                            jobs = job_scraper.search_jobs(search_skills, location, max_results=10)
                            
                            # Filter by skill match
                            filtered_jobs = job_scraper.filter_jobs_by_skills(jobs, search_skills, min_match)
                            
                            # Store results
                            st.session_state.job_results = filtered_jobs
                            
                            if filtered_jobs:
                                st.success(f"Found {len(filtered_jobs)} matching jobs!")
                            else:
                                st.info("No jobs found matching your criteria. Try broadening your search.")
        
        with col2:
            # Job search tips
            with st.expander("Job Search Tips", expanded=True):
                st.markdown("""
                ### Tips for better results:
                
                - Use specific skills rather than job titles
                - Include both technical and soft skills
                - Try different combinations of skills
                - Include industry-specific terminology
                - Searching without location will include remote jobs
                """)
    
    # Display job results
    if st.session_state.user_id and st.session_state.job_results:
        st.subheader("Job Matches")
        
        # Create match distribution chart
        match_values = [job.get('skills_match', 0) for job in st.session_state.job_results]
        
        if match_values:
            fig = px.histogram(
                x=match_values,
                nbins=10,
                labels={'x': 'Match Percentage', 'y': 'Number of Jobs'},
                title='Skill Match Distribution',
                color_discrete_sequence=['#3366CC']
            )
            fig.update_layout(
                xaxis_title="Match Percentage",
                yaxis_title="Number of Jobs",
                bargap=0.1
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Job listing view toggles
        view_option = st.radio(
            "View jobs as:",
            ["Cards", "Table"],
            horizontal=True
        )
        
        # Sort options
        sort_option = st.selectbox(
            "Sort by:",
            ["Match Percentage (High to Low)", "Date Posted (Newest First)", "Company"]
        )
        
        # Sort jobs
        sorted_jobs = st.session_state.job_results.copy()
        if sort_option == "Match Percentage (High to Low)":
            sorted_jobs.sort(key=lambda job: job.get('skills_match', 0), reverse=True)
        elif sort_option == "Date Posted (Newest First)":
            # Convert to datetime for sorting
            for job in sorted_jobs:
                try:
                    job['date_obj'] = datetime.strptime(job.get('date_posted', '2000-01-01'), '%Y-%m-%d')
                except:
                    job['date_obj'] = datetime(2000, 1, 1)
            sorted_jobs.sort(key=lambda job: job.get('date_obj', datetime(2000, 1, 1)), reverse=True)
        else:  # Company
            sorted_jobs.sort(key=lambda job: job.get('company', '').lower())
        
        # Display jobs according to view option
        if view_option == "Cards":
            for job in sorted_jobs:
                with st.expander(f"{job.get('title', 'Job Title')} - {job.get('company', 'Company')} ({job.get('skills_match', 0)}% match)"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Title:** {job.get('title', 'N/A')}")
                        st.markdown(f"**Company:** {job.get('company', 'N/A')}")
                        st.markdown(f"**Location:** {job.get('location', 'N/A')}")
                        st.markdown(f"**Salary:** {job.get('salary', 'N/A')}")
                        st.markdown(f"**Posted:** {job.get('date_posted', 'N/A')}")
                        
                        st.markdown("### Description")
                        st.markdown(job.get('description', 'No description available.'))
                        
                        st.markdown("### Requirements")
                        st.markdown(job.get('requirements', 'No requirements specified.'))
                    
                    with col2:
                        # Match percentage visualization
                        match_pct = job.get('skills_match', 0)
                        st.markdown(f"### Match: {match_pct}%")
                        
                        # Progress bar for match
                        st.progress(match_pct / 100.0)
                        
                        # Buttons for job actions
                        job_id = job.get('id', f"job_{hash(str(job))}")
                        if st.button("Visit Job", key=f"visit_{job_id}"):
                            st.markdown(f"[Visit Job Posting]({job.get('url', '#')})")
                        
                        if st.button("Save Job", key=f"save_{job_id}"):
                            saved_id = save_job_search(st.session_state.user_id, job)
                            if saved_id:
                                st.success("Job saved to your profile!")
                            else:
                                st.error("Failed to save job. Please try again.")
        else:  # Table view
            # Create a DataFrame for display
            job_data = []
            for job in sorted_jobs:
                job_data.append({
                    "Title": job.get('title', 'N/A'),
                    "Company": job.get('company', 'N/A'),
                    "Location": job.get('location', 'N/A'),
                    "Match %": job.get('skills_match', 0),
                    "Posted Date": job.get('date_posted', 'N/A'),
                    "Salary": job.get('salary', 'N/A')
                })
            
            if job_data:
                df = pd.DataFrame(job_data)
                st.dataframe(df, use_container_width=True)
    
    # Saved jobs section
    if st.session_state.user_id:
        with st.expander("View Saved Jobs", expanded=False):
            saved_jobs = user_skills.get_saved_jobs(st.session_state.user_id)
            
            if saved_jobs:
                for i, saved_job in enumerate(saved_jobs):
                    job = saved_job['job']
                    match_pct = saved_job['match_percentage']
                    
                    st.markdown(f"### {job['title']} - {job['company']}")
                    st.markdown(f"**Location:** {job['location']} | **Match:** {match_pct}% | **Saved on:** {saved_job['saved_at'][:10]}")
                    
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(job['description'][:200] + "..." if len(job['description']) > 200 else job['description'])
                    
                    with col2:
                        if st.button("Remove", key=f"remove_saved_{i}"):
                            if user_skills.delete_saved_job(st.session_state.user_id, saved_job['saved_job_id']):
                                st.success("Job removed from saved jobs!")
                                st.rerun()
                            else:
                                st.error("Failed to remove job. Please try again.")
            else:
                st.info("You haven't saved any jobs yet. Search for jobs and save them to view them here.")
    
def save_job_search(user_id, job_data):
    """Save a job to the user's saved jobs"""
    try:
        match_percentage = job_data.get('skills_match', 0)
        saved_job_id = user_skills.save_job_for_user(
            user_id,
            job_data,
            match_percentage
        )
        return saved_job_id
    except Exception as e:
        st.error(f"Error saving job: {e}")
        return None