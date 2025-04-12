import os
import re
import streamlit as st
import pandas as pd
import docx
import pdfplumber
import json
from datetime import datetime

# Import custom modules
import utils
import database
from database import get_session, Resume

# Check if database is available
DATABASE_AVAILABLE = True
try:
    # Test database connection
    session = get_session()
    session.close()
except Exception as e:
    print(f"Database error: {e}")
    DATABASE_AVAILABLE = False

# Constants
RESUME_DATA_DIR = "data/resumes"
os.makedirs(RESUME_DATA_DIR, exist_ok=True)

# Regular expressions for extraction
PHONE_PATTERN = r'(?:\+\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'
EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
LINKEDIN_PATTERN = r'linkedin\.com/in/[a-zA-Z0-9_-]+'
GITHUB_PATTERN = r'github\.com/[a-zA-Z0-9_-]+'
TWITTER_PATTERN = r'twitter\.com/[a-zA-Z0-9_-]+'
NAME_PATTERNS = [
    r'^\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\s*$',  # Simple name at beginning of line
    r'^\s*name:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\s*$',  # "Name: John Doe"
    r'^\s*([A-Z][A-Z\s]+)\s*$',  # ALL CAPS NAME
]

def extract_text_from_docx(file_path):
    """Extract text from a .docx file"""
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file"""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_contact_info(text):
    """Extract contact information from resume text"""
    # Extract basic contact info
    phone_matches = re.findall(PHONE_PATTERN, text)
    email_matches = re.findall(EMAIL_PATTERN, text)
    linkedin_matches = re.findall(LINKEDIN_PATTERN, text)
    github_matches = re.findall(GITHUB_PATTERN, text)
    twitter_matches = re.findall(TWITTER_PATTERN, text)
    
    # Extract name (this is more complex)
    name = extract_name(text)
    
    return {
        "name": name,
        "phone": phone_matches[0] if phone_matches else None,
        "email": email_matches[0] if email_matches else None,
        "linkedin": linkedin_matches[0] if linkedin_matches else None,
        "github": github_matches[0] if github_matches else None,
        "twitter": twitter_matches[0] if twitter_matches else None
    }

def extract_name(text):
    """Attempt to extract name from resume text - this is a simplified approach"""
    # Split into lines for better analysis
    lines = text.split('\n')
    
    # Try different name patterns on the first few lines
    for line in lines[:10]:  # Check first 10 lines
        for pattern in NAME_PATTERNS:
            match = re.match(pattern, line)
            if match:
                return match.group(1).strip()
    
    return None

def generate_profile_improvement_suggestions(contact_info):
    """Generate suggestions for improving social media profiles"""
    suggestions = {}
    
    # LinkedIn suggestions
    if contact_info.get('linkedin'):
        suggestions["linkedin"] = [
            "Ensure your LinkedIn headline clearly states your professional identity and value proposition",
            "Add a professional photo and background image that represents your industry",
            "Request recommendations from colleagues and managers",
            "Add specific metrics and achievements to your experience descriptions",
            "Join relevant industry groups and participate in discussions"
        ]
    else:
        suggestions["linkedin"] = [
            "Create a LinkedIn profile to increase your professional visibility",
            "Connect with colleagues and industry professionals",
            "Share your work and professional insights regularly"
        ]
    
    # GitHub suggestions
    if contact_info.get('github'):
        suggestions["github"] = [
            "Make sure your repositories have detailed README files",
            "Add descriptions and topics to your repositories",
            "Contribute to open-source projects to showcase your skills",
            "Pin your most impressive projects to your profile",
            "Complete your GitHub profile with a bio and contact information"
        ]
    else:
        suggestions["github"] = [
            "Create a GitHub profile to showcase your technical projects",
            "Contribute to open-source projects related to your field",
            "Use GitHub Pages to host a portfolio site"
        ]
    
    # Twitter suggestions
    if contact_info.get('twitter'):
        suggestions["twitter"] = [
            "Share industry insights and articles regularly",
            "Engage with thought leaders in your field",
            "Use relevant hashtags to increase visibility",
            "Balance professional content with personality",
            "Keep your profile professional with a clear bio and professional photo"
        ]
    else:
        suggestions["twitter"] = [
            "Consider creating a professional Twitter account to engage with industry trends",
            "Follow thought leaders in your field",
            "Share your professional insights and accomplishments"
        ]
    
    # General suggestions
    suggestions["general"] = [
        "Maintain consistency across all your social media profiles (photo, bio, expertise)",
        "Regularly update your profiles with recent achievements and projects",
        "Engage with your network by commenting and sharing valuable content",
        "Consider creating a personal website to serve as a comprehensive portfolio",
        "Use the same handle/username across platforms for brand consistency"
    ]
    
    return suggestions

def analyze_resume(file_path, file_extension):
    """Analyze a resume file and extract information"""
    # Extract text based on file type
    if file_extension == 'docx':
        text = extract_text_from_docx(file_path)
    elif file_extension == 'pdf':
        text = extract_text_from_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")
    
    # Extract contact information
    contact_info = extract_contact_info(text)
    
    # Generate suggestions for social media profiles
    suggestions = generate_profile_improvement_suggestions(contact_info)
    
    # Extract skills (simple approach)
    # Note: This is a very simplified approach. A more sophisticated approach
    # would use NLP techniques and a skills database.
    skills_section = extract_skills_section(text)
    
    # Return analysis results
    return {
        "contact_info": contact_info,
        "improvement_suggestions": suggestions,
        "extracted_text": text,
        "skills": skills_section
    }

def extract_skills_section(text):
    """Extract skills section from resume (simplified approach)"""
    skills = []
    
    # Look for skills section
    skill_patterns = [
        r'(?:SKILLS|Skills|skills|TECHNICAL SKILLS|Technical Skills|TECHNOLOGIES|Technologies)(?:[:\n])(.*?)(?:\n\n|\n[A-Z])',
        r'(?:SKILLS|Skills|skills)(?:[\s\n:]+)(.*?)(?:\n\n|\n[A-Z])'
    ]
    
    for pattern in skill_patterns:
        matches = re.search(pattern, text, re.DOTALL)
        if matches:
            skills_text = matches.group(1).strip()
            
            # Split skills by various delimiters
            skill_list = re.split(r'[,•|/\n]+', skills_text)
            skills = [skill.strip() for skill in skill_list if skill.strip()]
            break
    
    return skills

def save_resume_data(user_id, filename, analysis_results):
    """Save resume analysis results"""
    if DATABASE_AVAILABLE:
        try:
            # Save to database
            from utils import generate_id
            
            session = get_session()
            
            # Generate ID for resume
            resume_id = generate_id()
            
            # Create new resume record
            new_resume = Resume(
                id=resume_id,
                user_id=user_id,
                filename=filename,
                extracted_data=analysis_results["contact_info"],
                improvement_suggestions=analysis_results["improvement_suggestions"]
            )
            
            try:
                session.add(new_resume)
                session.commit()
                return resume_id
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
                
        except Exception as e:
            print(f"Database error saving resume: {e}")
            # Fall back to file-based storage
    
    # Use file-based storage
    resume_id = utils.generate_id()
    resume_data = {
        "id": resume_id,
        "user_id": user_id,
        "filename": filename,
        "analysis_results": analysis_results,
        "uploaded_at": datetime.now().isoformat()
    }
    
    # Create user's resume directory if it doesn't exist
    user_resume_dir = os.path.join(RESUME_DATA_DIR, user_id)
    os.makedirs(user_resume_dir, exist_ok=True)
    
    # Save resume data
    resume_file = os.path.join(user_resume_dir, f"{resume_id}.json")
    with open(resume_file, "w") as f:
        json.dump(resume_data, f, indent=2)
    
    return resume_id

def get_user_resumes(user_id):
    """Get all resumes for a user"""
    if DATABASE_AVAILABLE:
        try:
            session = get_session()
            
            try:
                # Query for user's resumes
                resumes = session.query(Resume).filter_by(user_id=user_id).all()
                
                return [{
                    "id": resume.id,
                    "filename": resume.filename,
                    "contact_info": resume.extracted_data,
                    "improvement_suggestions": resume.improvement_suggestions,
                    "uploaded_at": resume.uploaded_at.isoformat()
                } for resume in resumes]
            except Exception as e:
                raise e
            finally:
                session.close()
                
        except Exception as e:
            print(f"Database error getting resumes: {e}")
            # Fall back to file-based storage
    
    # Use file-based storage
    user_resume_dir = os.path.join(RESUME_DATA_DIR, user_id)
    
    # If user directory doesn't exist, return empty list
    if not os.path.exists(user_resume_dir):
        return []
    
    # Get all resume files
    resume_files = [f for f in os.listdir(user_resume_dir) if f.endswith('.json')]
    
    # Load resume data
    resumes = []
    for resume_file in resume_files:
        file_path = os.path.join(user_resume_dir, resume_file)
        with open(file_path, "r") as f:
            resume_data = json.load(f)
            resumes.append({
                "id": resume_data["id"],
                "filename": resume_data["filename"],
                "contact_info": resume_data["analysis_results"]["contact_info"],
                "improvement_suggestions": resume_data["analysis_results"]["improvement_suggestions"],
                "uploaded_at": resume_data["uploaded_at"]
            })
    
    return resumes

def get_resume_by_id(user_id, resume_id):
    """Get a specific resume by ID"""
    if DATABASE_AVAILABLE:
        try:
            session = get_session()
            
            try:
                # Query for specific resume
                resume = session.query(Resume).filter_by(id=resume_id, user_id=user_id).first()
                
                if resume:
                    return {
                        "id": resume.id,
                        "filename": resume.filename,
                        "contact_info": resume.extracted_data,
                        "improvement_suggestions": resume.improvement_suggestions,
                        "uploaded_at": resume.uploaded_at.isoformat()
                    }
                
                return None
            except Exception as e:
                raise e
            finally:
                session.close()
                
        except Exception as e:
            print(f"Database error getting resume: {e}")
            # Fall back to file-based storage
    
    # Use file-based storage
    user_resume_dir = os.path.join(RESUME_DATA_DIR, user_id)
    resume_file = os.path.join(user_resume_dir, f"{resume_id}.json")
    
    # If file doesn't exist, return None
    if not os.path.exists(resume_file):
        return None
    
    # Load resume data
    with open(resume_file, "r") as f:
        resume_data = json.load(f)
        return {
            "id": resume_data["id"],
            "filename": resume_data["filename"],
            "contact_info": resume_data["analysis_results"]["contact_info"],
            "improvement_suggestions": resume_data["analysis_results"]["improvement_suggestions"],
            "uploaded_at": resume_data["uploaded_at"]
        }

def render_resume_analyzer_ui():
    """Render the Resume Analyzer UI in the Streamlit app"""
    st.title("Resume Analyzer & Profile Improvement")
    
    st.markdown("""
    ## How It Works:
    
    1. **Upload Your Resume**: Submit your PDF or DOCX resume using the upload button below
    2. **AI Analysis**: We'll extract key information like your name, contact details, and social media profiles
    3. **Profile Recommendations**: Receive personalized suggestions to improve your LinkedIn, GitHub, and other professional profiles
    4. **Skills Assessment**: Get insights about your current skills and how they match with job market demands
    
    This tool helps you optimize your online presence and make your profiles more attractive to recruiters.
    """)
    
    # User authentication check
    if "user_id" not in st.session_state or not st.session_state.user_id:
        st.warning("Please create or log in to your account to use the Resume Analyzer.")
        
        # Simple login/signup form
        with st.expander("Sign Up / Log In"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Create Account")
                new_name = st.text_input("Name", key="new_name")
                new_email = st.text_input("Email", key="new_email")
                new_skills = st.text_input("Skills (comma separated)", key="new_skills")
                
                if st.button("Create Account"):
                    if new_name and new_email:
                        # Convert skills string to list
                        skills_list = [skill.strip() for skill in new_skills.split(",") if skill.strip()]
                        
                        # Create user
                        import user_skills
                        user_id = user_skills.create_user(new_name, new_email, skills_list)
                        
                        # Update session state
                        st.session_state.user_id = user_id
                        st.session_state.user_email = new_email
                        st.session_state.user_skills = skills_list
                        
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error("Please enter your name and email.")
            
            with col2:
                st.subheader("Log In")
                email = st.text_input("Email", key="login_email")
                
                if st.button("Log In"):
                    if email:
                        # Find user by email
                        import user_skills
                        user_data = user_skills.get_user_by_email(email)
                        
                        if user_data:
                            # Update session state
                            st.session_state.user_id = user_data["id"]
                            st.session_state.user_email = user_data["email"]
                            st.session_state.user_skills = user_data.get("skills", [])
                            
                            st.success("Logged in successfully!")
                            st.rerun()
                        else:
                            st.error("User not found. Please check your email or create an account.")
                    else:
                        st.error("Please enter your email.")
        
        return
    
    # If user is logged in, show resume analyzer
    st.success(f"Logged in as {st.session_state.user_email}")
    
    # Show previously uploaded resumes
    st.subheader("Your Resumes")
    
    # Get user's resumes
    resumes = get_user_resumes(st.session_state.user_id)
    
    if resumes:
        # Display resumes in a table
        resume_data = [{
            "Filename": r["filename"],
            "Uploaded": r["uploaded_at"][:19].replace("T", " "),
            "ID": r["id"]
        } for r in resumes]
        
        df = pd.DataFrame(resume_data)
        st.dataframe(df[["Filename", "Uploaded"]], hide_index=True)
        
        # Select resume to view
        selected_resume_id = st.selectbox(
            "Select a resume to view details",
            options=[r["id"] for r in resumes],
            format_func=lambda x: next((r["filename"] for r in resumes if r["id"] == x), x)
        )
        
        if selected_resume_id:
            show_resume_details(st.session_state.user_id, selected_resume_id)
    else:
        st.info("You haven't uploaded any resumes yet.")
    
    # Upload new resume
    st.subheader("Upload New Resume")
    
    uploaded_file = st.file_uploader("Choose a resume file", type=["pdf", "docx"])
    
    if uploaded_file:
        # Save file to temporary location
        file_extension = uploaded_file.name.split(".")[-1].lower()
        temp_file_path = os.path.join(RESUME_DATA_DIR, f"temp_{st.session_state.user_id}.{file_extension}")
        
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Process and analyze the resume
        try:
            st.info("Analyzing resume...")
            analysis_results = analyze_resume(temp_file_path, file_extension)
            
            # Save resume data
            resume_id = save_resume_data(
                st.session_state.user_id,
                uploaded_file.name,
                analysis_results
            )
            
            # Remove temporary file
            os.remove(temp_file_path)
            
            st.success("Resume analyzed successfully!")
            
            # Show analysis results
            show_resume_details(st.session_state.user_id, resume_id)
            
            # Refresh page to update resume list
            st.rerun()
        except Exception as e:
            st.error(f"Error analyzing resume: {str(e)}")
            
            # Remove temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

def show_resume_details(user_id, resume_id):
    """Show resume analysis details"""
    # Get resume data
    resume_data = get_resume_by_id(user_id, resume_id)
    
    if not resume_data:
        st.error("Resume not found.")
        return
    
    # Display contact information
    st.subheader("Extracted Information")
    
    contact_info = resume_data["contact_info"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Name:** {contact_info.get('name', 'Not found')}")
        st.markdown(f"**Email:** {contact_info.get('email', 'Not found')}")
        st.markdown(f"**Phone:** {contact_info.get('phone', 'Not found')}")
    
    with col2:
        st.markdown(f"**LinkedIn:** {contact_info.get('linkedin', 'Not found')}")
        st.markdown(f"**GitHub:** {contact_info.get('github', 'Not found')}")
        st.markdown(f"**Twitter:** {contact_info.get('twitter', 'Not found')}")
    
    # Display improvement suggestions
    st.subheader("Profile Improvement Suggestions")
    
    suggestions = resume_data["improvement_suggestions"]
    
    if suggestions:
        tabs = st.tabs(["LinkedIn", "GitHub", "Twitter", "General"])
        
        with tabs[0]:
            if "linkedin" in suggestions:
                for suggestion in suggestions["linkedin"]:
                    st.markdown(f"- {suggestion}")
            else:
                st.info("No LinkedIn suggestions available.")
        
        with tabs[1]:
            if "github" in suggestions:
                for suggestion in suggestions["github"]:
                    st.markdown(f"- {suggestion}")
            else:
                st.info("No GitHub suggestions available.")
        
        with tabs[2]:
            if "twitter" in suggestions:
                for suggestion in suggestions["twitter"]:
                    st.markdown(f"- {suggestion}")
            else:
                st.info("No Twitter suggestions available.")
        
        with tabs[3]:
            if "general" in suggestions:
                for suggestion in suggestions["general"]:
                    st.markdown(f"- {suggestion}")
            else:
                st.info("No general suggestions available.")
    else:
        st.info("No improvement suggestions available.")

# No need to initialize database here since we're importing from database.py