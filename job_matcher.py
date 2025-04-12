import streamlit as st
import pandas as pd
import random
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# Custom styling for job matcher components
job_matcher_style = """
<style>
.skill-pill {
    background: linear-gradient(90deg, #9146FF, #6772E5);
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    margin: 5px;
    display: inline-block;
    font-size: 0.9em;
    font-weight: bold;
    box-shadow: 0 0 10px rgba(145, 70, 255, 0.6);
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
    animation: skillGlow 3s infinite;
}

.skill-pill:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 15px rgba(145, 70, 255, 0.9);
}

@keyframes skillGlow {
    0% { box-shadow: 0 0 8px rgba(145, 70, 255, 0.5); }
    50% { box-shadow: 0 0 15px rgba(145, 70, 255, 0.8); }
    100% { box-shadow: 0 0 8px rgba(145, 70, 255, 0.5); }
}

.job-match-header {
    background: linear-gradient(90deg, rgba(145, 70, 255, 0.1), rgba(103, 114, 229, 0.1));
    padding: 10px;
    border-radius: 8px;
    border-left: 4px solid #9146FF;
}

.job-card {
    background: rgba(30, 37, 49, 0.8);
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 4px 15px rgba(145, 70, 255, 0.3);
    border: 1px solid rgba(145, 70, 255, 0.3);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.job-card:before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 5px;
    background: linear-gradient(90deg, #9146FF, #6772E5);
    opacity: 0.7;
}

.job-card:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 8px 25px rgba(145, 70, 255, 0.5), 0 0 20px rgba(103, 114, 229, 0.3);
    border: 1px solid rgba(145, 70, 255, 0.6);
    animation: cardPulse 2s infinite;
}

@keyframes cardPulse {
    0% { box-shadow: 0 8px 20px rgba(145, 70, 255, 0.4); }
    50% { box-shadow: 0 8px 30px rgba(145, 70, 255, 0.6), 0 0 20px rgba(103, 114, 229, 0.4); }
    100% { box-shadow: 0 8px 20px rgba(145, 70, 255, 0.4); }
}

/* Animation for skill addition */
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(10px);}
    to {opacity: 1; transform: translateY(0);}
}

.skill-item {
    animation: fadeIn 0.3s ease-out forwards;
}
</style>
"""

def render_job_matcher_ui():
    """Render the Job Matcher UI in the Streamlit app"""
    # Apply custom styling
    st.markdown(job_matcher_style, unsafe_allow_html=True)
    
    st.subheader("Match Your Skills to Job Opportunities")
    
    # User skills input section
    st.write("Enter your skills to find matching job opportunities:")
    
    # Initialize skills in session state if needed
    if "user_skills" not in st.session_state:
        st.session_state.user_skills = []
    
    # Skill input
    col1, col2 = st.columns([3, 1])
    with col1:
        new_skill = st.text_input("Add a skill:", key="new_skill_input")
    with col2:
        if st.button("Add Skill", use_container_width=True):
            if new_skill and new_skill not in st.session_state.user_skills:
                st.session_state.user_skills.append(new_skill)
                # Reset input by using rerun
                st.rerun()
    
    # Display current skills with delete buttons
    if st.session_state.user_skills:
        st.markdown("<div class='job-match-header'><h4>Your skills:</h4></div>", unsafe_allow_html=True)
        
        # Create columns for skills display
        cols = st.columns(3)
        for i, skill in enumerate(st.session_state.user_skills):
            col_idx = i % 3
            with cols[col_idx]:
                # Create a button for each skill that allows removal with custom styling
                if st.button(f"❌ {skill}", key=f"remove_{i}", use_container_width=True):
                    st.session_state.user_skills.remove(skill)
                    st.rerun()
    
    # Job search section
    st.subheader("Find Job Matches")
    
    # Location input
    location = st.text_input("Location (optional):", "")
    
    # Industry selection
    industries = ["All Industries", "Technology", "Healthcare", "Finance", "Data & Analytics", "Artificial Intelligence", "Security"]
    industry = st.selectbox("Industry:", industries)
    
    # Experience level
    experience_levels = ["All Levels", "Entry Level", "Mid Level", "Senior Level"]
    experience = st.selectbox("Experience Level:", experience_levels)
    
    # Search button
    if st.button("Find Matching Jobs", use_container_width=True):
        if not st.session_state.user_skills:
            st.error("Please add at least one skill before searching for jobs.")
        else:
            # Generate example jobs based on user skills
            jobs = generate_example_jobs(st.session_state.user_skills, location, industry, experience)
            
            # Store in session state
            st.session_state.job_results = jobs
            
            # Display results
            display_job_results(jobs)
    
    # Display previous results if they exist
    elif "job_results" in st.session_state and st.session_state.job_results:
        display_job_results(st.session_state.job_results)

def display_job_results(jobs):
    """Display job search results"""
    st.markdown(f"<div class='job-match-header'><h3>Found {len(jobs)} matching jobs</h3></div>", unsafe_allow_html=True)
    
    if not jobs:
        st.info("No matching jobs found. Try adjusting your skills or filters.")
        return
    
    # Skills match visualization
    st.markdown("<h4 style='background: linear-gradient(90deg, rgba(145, 70, 255, 0.1), rgba(103, 114, 229, 0.05)); padding: 10px; border-radius: 5px;'>Skills Match Distribution:</h4>", unsafe_allow_html=True)
    
    # Extract match percentages for visualization
    match_data = [{"Job Title": job["title"], "Match %": job["match_percentage"]} for job in jobs]
    match_df = pd.DataFrame(match_data)
    
    fig = px.bar(
        match_df,
        x="Job Title",
        y="Match %",
        color="Match %",
        color_continuous_scale="viridis",
        title="Skills Match Percentage by Job"
    )
    # Update chart appearance to match theme
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FAFAFA"),
        title_font=dict(color="#FAFAFA", size=18),
        title_x=0.5,
        margin=dict(t=50, b=50, l=30, r=30)
    )
    fig.update_layout(xaxis_tickangle=-45)
    fig.update_traces(hovertemplate='%{y:.0f}%')
    fig.update_layout(yaxis_tickformat='.0f')
    st.plotly_chart(fig, use_container_width=True)
    
    # Job listings
    for i, job in enumerate(jobs):
        with st.expander(f"{job['title']} - {job['match_percentage']}% Match", expanded=i==0):
            # Apply job card styling
            st.markdown("<div class='job-card'>", unsafe_allow_html=True)
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Company:** {job['company']}")
                st.markdown(f"**Location:** {job['location']}")
                st.markdown(f"**Salary:** {job['salary_range'] if 'salary_range' in job else job.get('salary', 'Not specified')}")
                
                # Display skills as styled pills
                skills_html = ""
                required_skills = job.get('required_skills', job.get('skills_required', []))
                for skill in required_skills:
                    skills_html += f"<span class='skill-pill'>{skill}</span> "
                st.markdown(f"**Required Skills:** ", unsafe_allow_html=True)
                st.markdown(f"<div class='skill-item'>{skills_html}</div>", unsafe_allow_html=True)
                
                st.markdown(f"**Job Description:**")
                st.markdown(job['description'])
            
            with col2:
                st.metric("Skills Match", f"{job['match_percentage']}%")
                if "salary_number" in job:
                    st.metric("Annual Salary", f"${job['salary_number']:,}")
                
                # Save job button
                if st.button("Save Job", key=f"save_job_{i}", use_container_width=True):
                    save_job_search(None, job)
                    st.success("Job saved to your profile!")
            
            st.markdown("</div>", unsafe_allow_html=True)

def save_job_search(user_id, job_data):
    """Save a job to the user's saved jobs"""
    # Initialize saved jobs in session state if needed
    if "saved_jobs" not in st.session_state:
        st.session_state.saved_jobs = []
    
    # Add job to saved jobs
    st.session_state.saved_jobs.append(job_data)

def generate_example_jobs(user_skills, location="", industry="All Industries", experience="All Levels"):
    """Generate job listings based on user skills using pre-loaded job data"""
    # Load job data from the JSON file
    job_data_path = os.path.join("data", "job_data.json")
    try:
        with open(job_data_path, "r") as f:
            job_data = json.load(f)
            job_listings_data = job_data.get("job_listings", [])
    except Exception as e:
        st.error(f"Error loading job data: {e}")
        return []
    
    # If no data was loaded, return empty list
    if not job_listings_data:
        return []
    
    # Convert user skills to lowercase for case-insensitive matching
    user_skills_lower = [skill.lower() for skill in user_skills]
    
    # Calculate match percentages for each job
    scored_jobs = []
    
    for job in job_listings_data:
        # Skills match calculation
        job_skills = [skill.lower() for skill in job.get("skills_required", [])]
        matched_skills = [skill for skill in user_skills_lower if skill in job_skills]
        
        # Calculate basic match percentage based on skills overlap
        if job_skills:
            skill_match_percentage = (len(matched_skills) / len(job_skills)) * 100
        else:
            skill_match_percentage = 0
            
        # Location filtering
        location_match = True
        if location and location.lower() not in job.get("location", "").lower():
            location_match = False
            
        # Industry filtering
        industry_match = True
        if industry != "All Industries" and industry.lower() != job.get("industry", "").lower():
            industry_match = False
            
        # Experience level filtering
        experience_match = True
        if experience != "All Levels":
            job_experience = job.get("experience", "")
            if experience == "Entry Level" and "1-" not in job_experience and "0-" not in job_experience:
                experience_match = False
            elif experience == "Mid Level" and "3-" not in job_experience and "4-" not in job_experience:
                experience_match = False
            elif experience == "Senior Level" and "5-" not in job_experience and "6-" not in job_experience and "7-" not in job_experience:
                experience_match = False
        
        # Only include jobs that match all filters
        if location_match and industry_match and experience_match:
            # Add some randomness to make results interesting (±10%)
            randomness = random.uniform(-5, 5)
            final_match = min(99, max(60, skill_match_percentage + randomness))
            
            # Create the job entry with calculated match percentage
            job_entry = job.copy()
            job_entry["match_percentage"] = round(final_match)
            
            # Format data properly for display 
            job_entry["required_skills"] = job_entry.get("skills_required", [])
            
            scored_jobs.append((final_match, job_entry))
    
    # Sort by match percentage (highest first) and extract just the job data
    scored_jobs.sort(reverse=True, key=lambda x: x[0])
    matching_jobs = [job for _, job in scored_jobs]
    
    # Limit to 10 results 
    return matching_jobs[:10]