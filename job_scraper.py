import pandas as pd
import trafilatura
import json
import time
import re
from datetime import datetime
from urllib.parse import urljoin

# Constants
JOB_SITES = {
    "Indeed": "https://www.indeed.com/jobs?q={}&l={}",
    "LinkedIn": "https://www.linkedin.com/jobs/search/?keywords={}&location={}",
}

# Cache for storing scraped job data
JOB_CACHE_FILE = "job_cache.json"
job_cache = {}

def load_job_cache():
    """Load cached job data if available"""
    global job_cache
    try:
        with open(JOB_CACHE_FILE, 'r') as f:
            job_cache = json.load(f)
        print(f"Loaded {len(job_cache)} cached job entries")
    except FileNotFoundError:
        job_cache = {}
        save_job_cache()
        print("Created new job cache")

def save_job_cache():
    """Save job data to cache file"""
    with open(JOB_CACHE_FILE, 'w') as f:
        json.dump(job_cache, f)
    print(f"Saved {len(job_cache)} job entries to cache")

def get_website_text_content(url):
    """Get the main text content from a website"""
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            return text
        return None
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return None

def clean_job_data(text):
    """Extract and clean job information from scraped text"""
    if not text:
        return None
    
    # Basic cleaning
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Try to extract job information - this is a simplified version
    # In a production environment, you'd need more sophisticated parsing
    job_info = {
        'title': '',
        'company': '',
        'location': '',
        'salary': '',
        'description': text[:1000],  # Truncate description to avoid huge text blocks
        'requirements': '',
        'date_posted': '',
        'full_text': text
    }
    
    # Look for common patterns
    title_match = re.search(r'(?i)(job title|position):\s*([^\n]+)', text)
    if title_match:
        job_info['title'] = title_match.group(2).strip()
    
    company_match = re.search(r'(?i)(company|organization):\s*([^\n]+)', text)
    if company_match:
        job_info['company'] = company_match.group(2).strip()
    
    location_match = re.search(r'(?i)(location|place):\s*([^\n]+)', text)
    if location_match:
        job_info['location'] = location_match.group(2).strip()
    
    salary_match = re.search(r'(?i)(salary|compensation):\s*([^\n]+)', text)
    if salary_match:
        job_info['salary'] = salary_match.group(2).strip()
    
    requirements_match = re.search(r'(?i)(requirements|qualifications)[\s:]*([^\n]+(?:\n[^\n]+){0,10})', text)
    if requirements_match:
        job_info['requirements'] = requirements_match.group(2).strip()
    
    return job_info

def search_jobs(keywords, location="", max_results=50, use_cache=True):
    """Search for jobs matching the given keywords and location"""
    search_key = f"{keywords}_{location}".lower().replace(' ', '_')
    
    # Check cache first if enabled
    if use_cache and search_key in job_cache:
        cache_time = job_cache[search_key].get('timestamp', 0)
        current_time = time.time()
        # Use cache if it's less than 24 hours old
        if current_time - cache_time < 86400:  # 24 hours in seconds
            print(f"Using cached data for '{keywords}' in '{location}'")
            return job_cache[search_key].get('jobs', [])
    
    all_jobs = []
    
    # For demo purposes, generate some mock jobs based on the keywords
    # In a real implementation, you would scrape actual job sites
    example_jobs = generate_example_jobs(keywords, location, max_results)
    all_jobs.extend(example_jobs)
    
    # Save to cache
    job_cache[search_key] = {
        'timestamp': time.time(),
        'jobs': all_jobs
    }
    save_job_cache()
    
    return all_jobs

def generate_example_jobs(keywords, location, count=10):
    """Generate example job listings based on keywords for demonstration purposes"""
    skills = keywords.split(',')
    primary_skill = skills[0].strip() if skills else "general"
    
    # Create job titles based on the primary skill
    job_titles = [
        f"{primary_skill.title()} Developer",
        f"Senior {primary_skill.title()} Engineer",
        f"{primary_skill.title()} Analyst",
        f"{primary_skill.title()} Consultant",
        f"Lead {primary_skill.title()} Specialist",
        f"{primary_skill.title()} Project Manager",
        f"{primary_skill.title()} Architect",
        f"Junior {primary_skill.title()} Developer",
        f"{primary_skill.title()} Designer",
        f"{primary_skill.title()} Support Specialist"
    ]
    
    companies = [
        "TechCorp Inc.", "Innovative Solutions", "Global Systems", 
        "NextGen Tech", "Future Software", "CodeMasters", 
        "Digital Dynamics", "Tech Ventures", "ByteWorks", "DataSphere"
    ]
    
    locations = [location] * 5 + ["Remote", "New York, NY", "San Francisco, CA", "Austin, TX", "Seattle, WA"]
    
    salaries = [
        "$70,000 - $90,000", "$90,000 - $120,000", "$120,000 - $150,000",
        "$80,000 - $100,000", "$100,000 - $130,000", "Competitive",
        "$85,000 - $115,000", "$75,000 - $95,000", "$110,000 - $140,000", "DOE"
    ]
    
    jobs = []
    
    for i in range(min(count, 10)):
        # Create a requirements string that includes the original keywords
        requirements = f"- Proficiency in {primary_skill}\n"
        for skill in skills[1:]:
            if skill.strip():
                requirements += f"- Experience with {skill.strip()}\n"
        
        requirements += f"- {3 + i} years of software development experience\n"
        requirements += "- Bachelor's degree in Computer Science or related field\n"
        requirements += "- Strong communication skills\n"
        
        job = {
            'id': f"job_{int(time.time())}_{i}",
            'title': job_titles[i % len(job_titles)],
            'company': companies[i % len(companies)],
            'location': locations[i % len(locations)],
            'salary': salaries[i % len(salaries)],
            'description': f"We are seeking a talented {job_titles[i % len(job_titles)]} to join our team. "
                          f"You will be working on cutting-edge projects using {', '.join(skill.strip() for skill in skills if skill.strip())}. "
                          f"This is an exciting opportunity to grow your career in a dynamic environment.",
            'requirements': requirements,
            'date_posted': (datetime.now().replace(day=datetime.now().day - (i % 14))).strftime('%Y-%m-%d'),
            'skills_match': calculate_skill_match(skills, skills),  # Full match for demo
            'url': f"https://example.com/jobs/{i}_{primary_skill.lower().replace(' ', '_')}"
        }
        jobs.append(job)
    
    return jobs

def calculate_skill_match(job_skills, user_skills):
    """Calculate the match percentage between job skills and user skills"""
    if not job_skills or not user_skills:
        return 0
    
    # Convert to lowercase for comparison
    job_skills_lower = [skill.lower().strip() for skill in job_skills if skill.strip()]
    user_skills_lower = [skill.lower().strip() for skill in user_skills if skill.strip()]
    
    # Count matches
    matches = sum(1 for skill in user_skills_lower if any(job_skill in skill or skill in job_skill for job_skill in job_skills_lower))
    
    # Calculate percentage
    if len(user_skills_lower) > 0:
        match_percentage = (matches / len(user_skills_lower)) * 100
    else:
        match_percentage = 0
    
    return min(round(match_percentage), 100)  # Cap at 100%

def filter_jobs_by_skills(jobs, skills, min_match=0):
    """Filter jobs by required skills and minimum match percentage"""
    user_skills = [skill.strip() for skill in skills.split(',') if skill.strip()]
    
    filtered_jobs = []
    for job in jobs:
        # Extract skills from job requirements
        job_skills = []
        if 'requirements' in job:
            # Simple extraction - in a real app, this would be more sophisticated
            requirements = job['requirements']
            if isinstance(requirements, str):
                lines = requirements.split('\n')
                for line in lines:
                    if '-' in line:
                        skill_part = line.split('-', 1)[1].strip()
                        # Extract just the skill name (without "proficiency in" etc.)
                        skill_parts = re.findall(r'(?:proficiency|experience|knowledge)\s+(?:in|with)\s+([^,\.]+)', skill_part.lower())
                        if skill_parts:
                            job_skills.extend(skill_parts)
                        else:
                            # If no specific pattern found, use the whole skill part
                            job_skills.append(skill_part)
        
        # Calculate match percentage
        match_percentage = calculate_skill_match(job_skills, user_skills)
        
        # Add match percentage to job info
        job_copy = job.copy()
        job_copy['skills_match'] = match_percentage
        
        # Filter by minimum match
        if match_percentage >= min_match:
            filtered_jobs.append(job_copy)
    
    # Sort by match percentage (descending)
    filtered_jobs.sort(key=lambda j: j['skills_match'], reverse=True)
    
    return filtered_jobs

# Initialize cache when module is imported
load_job_cache()