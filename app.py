import streamlit as st
import pandas as pd
import os
import sample_data
from datetime import datetime
import user_skills
import job_matcher
import utils

# Create data directories if they don't exist
os.makedirs("data", exist_ok=True)
os.makedirs("data/resumes", exist_ok=True)
os.makedirs("data/interview_questions", exist_ok=True)
os.makedirs("data/users", exist_ok=True)

# Initialize database
try:
    import database
    st.session_state.using_database = True
except ImportError:
    st.session_state.using_database = False

# Set page configuration
st.set_page_config(
    page_title="IVCA - Intelligent Visualization & Career Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Hide default Streamlit menu and apply custom gradient styling
custom_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Apply gradient background */
.stApp {
    background: linear-gradient(to bottom right, #0E1117, #232952);
    background-image: url('assets/gradient-bg.svg');
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
    background-blend-mode: soft-light;
}

/* Style headers */
h1, h2, h3, h4, h5 {
    color: #EAEAEA;
    background: linear-gradient(90deg, #9146FF, #6772E5);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: bold;
}

/* Style buttons with INTENSE glow effect */
div.stButton > button {
    background: linear-gradient(90deg, #9146FF, #6772E5);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: bold;
    box-shadow: 0 0 20px rgba(145, 70, 255, 0.7), 0 0 30px rgba(103, 114, 229, 0.4);
    transition: all 0.2s ease;
    position: relative;
    z-index: 1;
    overflow: hidden;
}

div.stButton > button:before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, rgba(145, 70, 255, 0.5), rgba(103, 114, 229, 0.5));
    z-index: -1;
    transition: opacity 0.3s ease;
    opacity: 0;
}

div.stButton > button:hover {
    background: linear-gradient(90deg, #6772E5, #9146FF);
    border: none;
    box-shadow: 0 0 25px rgba(145, 70, 255, 0.9), 0 0 40px rgba(103, 114, 229, 0.6);
    transform: translateY(-5px) scale(1.03);
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

div.stButton > button:hover:before {
    opacity: 1;
}

div.stButton > button:active {
    transform: translateY(-2px) scale(0.98);
    box-shadow: 0 0 15px rgba(145, 70, 255, 0.6);
}

/* Style sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(15,20,30,0.95) 0%, rgba(28,35,65,0.9) 100%);
    border-right: 1px solid rgba(145, 70, 255, 0.2);
    box-shadow: 5px 0 15px rgba(0,0,0,0.2);
}

/* Style sidebar buttons with SUPER INTENSE glow */
[data-testid="stSidebar"] div.stButton > button {
    background: rgba(30, 37, 49, 0.5);
    border: 1px solid rgba(145, 70, 255, 0.7);
    box-shadow: 0 0 15px rgba(145, 70, 255, 0.6), 0 0 30px rgba(103, 114, 229, 0.3);
    transition: all 0.2s ease;
    margin-bottom: 10px;
    position: relative;
    overflow: hidden;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { box-shadow: 0 0 15px rgba(145, 70, 255, 0.6), 0 0 20px rgba(103, 114, 229, 0.3); }
    50% { box-shadow: 0 0 20px rgba(145, 70, 255, 0.8), 0 0 30px rgba(103, 114, 229, 0.5); }
    100% { box-shadow: 0 0 15px rgba(145, 70, 255, 0.6), 0 0 20px rgba(103, 114, 229, 0.3); }
}

[data-testid="stSidebar"] div.stButton > button:after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
        to bottom right,
        rgba(255, 255, 255, 0) 0%,
        rgba(255, 255, 255, 0) 40%,
        rgba(255, 255, 255, 0.4) 50%,
        rgba(255, 255, 255, 0) 60%,
        rgba(255, 255, 255, 0) 100%
    );
    transform: rotate(45deg);
    transition: all 0.3s ease;
    opacity: 0;
}

[data-testid="stSidebar"] div.stButton > button:hover {
    background: rgba(50, 57, 69, 0.8);
    border: 1px solid rgba(145, 70, 255, 1);
    box-shadow: 0 0 25px rgba(145, 70, 255, 0.9), 0 0 40px rgba(103, 114, 229, 0.7), inset 0 0 15px rgba(145, 70, 255, 0.5);
    transform: translateY(-3px) scale(1.05);
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.7);
    color: white;
}

[data-testid="stSidebar"] div.stButton > button:hover:after {
    opacity: 1;
    left: 100%;
    top: 100%;
    transition: all 0.7s ease-in-out;
}

/* Add subtle border glow to containers */
.css-1r6slb0, .css-keje6w, .css-1cpxqw2 {
    border: 1px solid rgba(145, 70, 255, 0.2);
    border-radius: 5px;
    box-shadow: 0 0 10px rgba(145, 70, 255, 0.1);
}

/* Style metrics */
[data-testid="stMetricValue"] {
    font-weight: bold;
    background: linear-gradient(90deg, #9146FF, #6772E5);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Glassmorphism for cards */
div.stCard, div.element-container div.stAlert {
    background: rgba(30, 37, 49, 0.7) !important;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(145, 70, 255, 0.2);
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

/* Animation for elements on hover */
.stExpander:hover {
    transform: translateY(-2px);
    transition: transform 0.3s ease;
}

/* Glowing accent elements */
.st-emotion-cache-16txtl3 h1, .st-emotion-cache-16txtl3 h2 {
    text-shadow: 0 0 10px rgba(145, 70, 255, 0.3);
}

/* Glowing accents for navigation */
.st-emotion-cache-16idsys p {
    text-shadow: 0 0 5px rgba(145, 70, 255, 0.5);
}

/* Enhanced sidebar navigation with glowing effects */
[data-testid="stSidebarNavItems"] {
    padding-top: 20px;
}

[data-testid="stSidebarNavItems"] div {
    transition: all 0.3s ease;
    position: relative;
    border-radius: 5px;
    overflow: hidden;
    margin-bottom: 5px;
}

[data-testid="stSidebarNavItems"] div:hover {
    background: linear-gradient(90deg, rgba(145, 70, 255, 0.15), rgba(103, 114, 229, 0.1));
    box-shadow: 0 0 15px rgba(145, 70, 255, 0.3), inset 0 0 10px rgba(145, 70, 255, 0.2);
    transform: translateX(5px);
}

[data-testid="stSidebarNavItems"] div p {
    transition: all 0.3s ease;
}

[data-testid="stSidebarNavItems"] div:hover p {
    text-shadow: 0 0 8px rgba(255, 255, 255, 0.7);
    transform: scale(1.02);
    color: #FFFFFF !important;
}

/* Add glow effect to navigation items */
[data-testid="stSidebarNavItems"] a:hover {
    text-decoration: none;
    text-shadow: 0 0 10px rgba(145, 70, 255, 0.9);
}

/* Add pulsing border to active navigation item */
[data-testid="stSidebarNavItems"] [aria-selected="true"] {
    border-right: 3px solid #9146FF;
    box-shadow: 0 0 10px rgba(145, 70, 255, 0.7);
    animation: borderPulse 2s infinite;
}

@keyframes borderPulse {
    0% { border-right-color: rgba(145, 70, 255, 0.7); }
    50% { border-right-color: rgba(103, 114, 229, 0.9); }
    100% { border-right-color: rgba(145, 70, 255, 0.7); }
}

/* Style inputs for a more modern look */
.stTextInput > div > div > input {
    background-color: rgba(30, 37, 49, 0.7);
    border: 1px solid rgba(145, 70, 255, 0.3);
    border-radius: 8px;
    color: white;
    padding: 10px;
}

.stTextInput > div > div > input:focus {
    border: 1px solid rgba(145, 70, 255, 0.8);
    box-shadow: 0 0 10px rgba(145, 70, 255, 0.4);
}
</style>
"""
st.markdown(custom_style, unsafe_allow_html=True)

# Initialize session state if needed
if 'dataset' not in st.session_state:
    st.session_state.dataset = None
if 'dataset_name' not in st.session_state:
    st.session_state.dataset_name = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'user_skills' not in st.session_state:
    st.session_state.user_skills = []
if 'job_results' not in st.session_state:
    st.session_state.job_results = []

# Main page
def main():
    # Header with IVCA logo and title
    col1, col2 = st.columns([1, 5])
    with col1:
        try:
            st.image("assets/icon.svg", width=100)
        except:
            st.image("https://cdn.jsdelivr.net/gh/feathericons/feather@master/icons/bar-chart-2.svg", width=100)
    with col2:
        st.title("IVCA - Intelligent Visualization & Career Analysis")
        st.write("Combine data analytics with career planning to master your future")
    
    # Display data stats in main area if we have data
    if st.session_state.dataset is not None:
        display_data_stats()
    
    # Database status indicator
    if st.session_state.using_database:
        st.sidebar.success("✅ Database system active")
    
    # Main content sections
    st.header("Welcome to IVCA")
    
    # Introduction section
    st.markdown("""
    IVCA helps you analyze data and plan your career with intelligent tools:
    
    - **Data Visualization**: Create interactive charts and visualizations
    - **Career Analysis**: Analyze job trends and skill requirements
    - **Skill Assessment**: Evaluate your skills and get recommendations
    """)
    
    # Load demo dataset automatically if none is loaded
    if st.session_state.dataset is None:
        st.info("To get started, select a sample dataset below")
        load_default_dataset()
    
    # Navigation cards
    st.subheader("Quick Navigation")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📊 Data Analytics
        Analyze and visualize your data with interactive charts to gain valuable insights.
        """)
        st.button("Data Visualization", key="nav_viz", use_container_width=True, 
                 on_click=lambda: st.switch_page("pages/01_Data_Visualization.py"))
    
    with col2:
        st.markdown("""
        ### 🚀 Career Planning
        Analyze job market trends, match your skills to opportunities, and get personalized recommendations.
        """)
        col2a, col2b = st.columns(2)
        with col2a:
            st.button("Career Analysis", key="nav_career", use_container_width=True,
                     on_click=lambda: st.switch_page("pages/03_Career_Analysis.py"))
        with col2b:
            st.button("Skill Assessment", key="nav_skills", use_container_width=True,
                     on_click=lambda: st.switch_page("pages/04_Skill_Assessment.py"))
    
    with col3:
        col3a, col3b = st.columns(2)
        
        with col3a:
            st.markdown("""
            ### 📄 Resume Analysis
            Upload your resume to extract information and get personalized recommendations.
            """)
            st.button("Resume Analyzer", key="nav_resume", use_container_width=True,
                    on_click=lambda: st.switch_page("pages/05_Resume_Analyzer.py"))
        
        with col3b:
            st.markdown("""
            ### 💼 Interview Prep
            Practice common interview questions and simulate real interviews.
            """)
            st.button("Interview Prep", key="nav_interview", use_container_width=True,
                    on_click=lambda: st.switch_page("pages/06_Interview_Prep.py"))
    
    # Display getting started tips
    with st.expander("Getting Started Guide", expanded=False):
        st.markdown("""
        ### Getting Started with IVCA:
        
        1. **Explore Data Visualization**: Navigate to the Data Visualization page to create interactive charts
        2. **Analyze Career Trends**: View Career Analysis to understand job market trends and skill requirements
        3. **Assess Your Skills**: Take the skills assessment to identify areas for improvement and get recommendations
        4. **Upload Your Resume**: Use the Resume Analyzer to extract information and get personalized profile improvement suggestions
        
        Our platform is designed to be intuitive for all users, from beginners to advanced data analysts and job seekers.
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(f"© {datetime.now().year} IVCA - Intelligent Visualization & Career Analysis")

def display_data_stats():
    """Display stats about the current dataset in main area"""
    try:
        df = st.session_state.dataset
        
        # Create a metrics section
        st.subheader(f"Current Dataset: {st.session_state.dataset_name}")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Rows", f"{df.shape[0]:,}")
        with col2:
            st.metric("Columns", f"{df.shape[1]:,}")
        with col3:
            missing = df.isna().sum().sum()
            missing_pct = (missing / (df.shape[0] * df.shape[1])) * 100
            st.metric("Missing Values", f"{missing:,} ({missing_pct:.2f}%)")
        
        # Show data preview in an expander
        with st.expander("Data Preview"):
            st.dataframe(df.head(10))
            
    except Exception as e:
        st.error(f"Error displaying dataset info: {e}")

def load_default_dataset():
    """Load a default dataset to start with"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Load Job Market Data", use_container_width=True):
            sample_df = sample_data.load_sample_job_market_data()
            st.session_state.dataset = sample_df
            st.session_state.dataset_name = "Job Market Analysis"
            st.success("Job Market data loaded successfully!")
            st.rerun()
    
    with col2:
        if st.button("Load Skills Analysis Data", use_container_width=True):
            sample_df = sample_data.load_sample_skills_data()
            st.session_state.dataset = sample_df
            st.session_state.dataset_name = "Skills Analysis"
            st.success("Skills Analysis data loaded successfully!")
            st.rerun()
            
    with col3:
        if st.button("Load Sample Sales Data", use_container_width=True):
            sample_df = sample_data.load_sample_sales_data()
            st.session_state.dataset = sample_df
            st.session_state.dataset_name = "Sales Data"
            st.success("Sales data loaded successfully!")
            st.rerun()

if __name__ == "__main__":
    main()
