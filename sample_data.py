import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_sample_sales_data():
    """Load sample sales data"""
    # Generate dates for the past year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='W')
    
    # Create sample data
    regions = ['North', 'South', 'East', 'West']
    categories = ['Electronics', 'Clothing', 'Furniture', 'Food', 'Toys']
    
    data = []
    
    for date in dates:
        for region in regions:
            for category in categories:
                # Generate random sales data
                revenue = np.random.randint(5000, 50000)
                units = np.random.randint(50, 500)
                profit = revenue * np.random.uniform(0.1, 0.4)
                
                data.append({
                    'Date': date,
                    'Region': region,
                    'Category': category,
                    'Revenue': revenue,
                    'Units': units,
                    'Profit': round(profit, 2),
                    'Quarter': f"Q{pd.Timestamp(date).quarter}",
                    'Year': pd.Timestamp(date).year
                })
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    return df

def load_sample_job_market_data():
    """Load sample job market data"""
    # Sample job titles and skills
    job_titles = [
        'Data Scientist', 'Software Engineer', 'Product Manager',
        'Data Analyst', 'UX Designer', 'Front-end Developer',
        'Back-end Developer', 'DevOps Engineer', 'Business Analyst',
        'Machine Learning Engineer'
    ]
    
    skills = [
        'Python', 'SQL', 'JavaScript', 'Java', 'C++', 'React', 
        'Angular', 'AWS', 'Azure', 'Data Visualization', 'Machine Learning',
        'Deep Learning', 'NLP', 'Docker', 'Kubernetes', 'Git',
        'Agile', 'Scrum', 'Power BI', 'Tableau', 'Excel',
        'R', 'Statistics', 'Communication', 'Problem Solving'
    ]
    
    regions = ['US East', 'US West', 'US Central', 'Europe', 'Asia Pacific']
    
    # Generate sample data
    data = []
    
    for job_title in job_titles:
        # Assign relevant skills to each job title
        if 'Data Scientist' in job_title:
            job_skills = 'Python, SQL, Machine Learning, Statistics, R'
        elif 'Software Engineer' in job_title:
            job_skills = 'JavaScript, Java, Git, Docker, AWS'
        elif 'Product Manager' in job_title:
            job_skills = 'Agile, Scrum, Communication, Problem Solving'
        elif 'Data Analyst' in job_title:
            job_skills = 'SQL, Python, Excel, Power BI, Tableau'
        elif 'UX Designer' in job_title:
            job_skills = 'Figma, Sketch, User Research, Wireframing'
        elif 'Front-end Developer' in job_title:
            job_skills = 'HTML, CSS, JavaScript, React, Angular'
        elif 'Back-end Developer' in job_title:
            job_skills = 'Java, Python, SQL, APIs, Node.js'
        elif 'DevOps Engineer' in job_title:
            job_skills = 'Docker, Kubernetes, AWS, CI/CD, Linux'
        elif 'Business Analyst' in job_title:
            job_skills = 'SQL, Excel, Power BI, Requirements Gathering'
        elif 'Machine Learning Engineer' in job_title:
            job_skills = 'Python, TensorFlow, PyTorch, Deep Learning, NLP'
        else:
            # Random selection of skills for other job titles
            num_skills = np.random.randint(3, 8)
            job_skills = ', '.join(np.random.choice(skills, num_skills, replace=False))
        
        for region in regions:
            # Generate random job market data
            num_openings = np.random.randint(50, 500)
            avg_salary = np.random.randint(60000, 180000)
            growth_rate = np.random.uniform(0.01, 0.2)
            competition_score = np.random.uniform(1, 10)
            demand_score = np.random.uniform(1, 10)
            
            data.append({
                'JobTitle': job_title,
                'Region': region,
                'RequiredSkills': job_skills,
                'NumberOfOpenings': num_openings,
                'AverageSalary': avg_salary,
                'GrowthRate': round(growth_rate, 2),
                'CompetitionScore': round(competition_score, 1),  # 1-10 scale (10 is highest competition)
                'DemandScore': round(demand_score, 1),  # 1-10 scale (10 is highest demand)
                'DateCollected': datetime.now().strftime('%Y-%m-%d')
            })
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    return df

def load_sample_skills_data():
    """Load sample skills analysis data"""
    # Sample skills and categories
    skills_data = [
        {'Skill': 'Python', 'Category': 'Programming', 'Popularity': 95, 'GrowthRate': 0.15, 'AvgSalary': 120000},
        {'Skill': 'JavaScript', 'Category': 'Programming', 'Popularity': 92, 'GrowthRate': 0.12, 'AvgSalary': 115000},
        {'Skill': 'Java', 'Category': 'Programming', 'Popularity': 88, 'GrowthRate': 0.05, 'AvgSalary': 125000},
        {'Skill': 'SQL', 'Category': 'Data', 'Popularity': 90, 'GrowthRate': 0.08, 'AvgSalary': 110000},
        {'Skill': 'Machine Learning', 'Category': 'Data Science', 'Popularity': 87, 'GrowthRate': 0.18, 'AvgSalary': 135000},
        {'Skill': 'Data Visualization', 'Category': 'Data', 'Popularity': 82, 'GrowthRate': 0.1, 'AvgSalary': 105000},
        {'Skill': 'React', 'Category': 'Frontend', 'Popularity': 89, 'GrowthRate': 0.14, 'AvgSalary': 120000},
        {'Skill': 'Angular', 'Category': 'Frontend', 'Popularity': 78, 'GrowthRate': 0.06, 'AvgSalary': 115000},
        {'Skill': 'Vue.js', 'Category': 'Frontend', 'Popularity': 75, 'GrowthRate': 0.12, 'AvgSalary': 110000},
        {'Skill': 'Node.js', 'Category': 'Backend', 'Popularity': 85, 'GrowthRate': 0.1, 'AvgSalary': 118000},
        {'Skill': 'Django', 'Category': 'Backend', 'Popularity': 70, 'GrowthRate': 0.08, 'AvgSalary': 115000},
        {'Skill': 'Flask', 'Category': 'Backend', 'Popularity': 65, 'GrowthRate': 0.09, 'AvgSalary': 112000},
        {'Skill': 'AWS', 'Category': 'Cloud', 'Popularity': 88, 'GrowthRate': 0.15, 'AvgSalary': 130000},
        {'Skill': 'Azure', 'Category': 'Cloud', 'Popularity': 82, 'GrowthRate': 0.14, 'AvgSalary': 128000},
        {'Skill': 'GCP', 'Category': 'Cloud', 'Popularity': 76, 'GrowthRate': 0.16, 'AvgSalary': 132000},
        {'Skill': 'Docker', 'Category': 'DevOps', 'Popularity': 84, 'GrowthRate': 0.13, 'AvgSalary': 125000},
        {'Skill': 'Kubernetes', 'Category': 'DevOps', 'Popularity': 80, 'GrowthRate': 0.15, 'AvgSalary': 132000},
        {'Skill': 'CI/CD', 'Category': 'DevOps', 'Popularity': 78, 'GrowthRate': 0.12, 'AvgSalary': 120000},
        {'Skill': 'TensorFlow', 'Category': 'Data Science', 'Popularity': 72, 'GrowthRate': 0.14, 'AvgSalary': 138000},
        {'Skill': 'PyTorch', 'Category': 'Data Science', 'Popularity': 68, 'GrowthRate': 0.16, 'AvgSalary': 140000},
        {'Skill': 'NLP', 'Category': 'Data Science', 'Popularity': 65, 'GrowthRate': 0.17, 'AvgSalary': 142000},
        {'Skill': 'Power BI', 'Category': 'Data', 'Popularity': 75, 'GrowthRate': 0.09, 'AvgSalary': 105000},
        {'Skill': 'Tableau', 'Category': 'Data', 'Popularity': 78, 'GrowthRate': 0.08, 'AvgSalary': 108000},
        {'Skill': 'Excel', 'Category': 'Data', 'Popularity': 85, 'GrowthRate': 0.03, 'AvgSalary': 90000},
        {'Skill': 'Git', 'Category': 'Tools', 'Popularity': 90, 'GrowthRate': 0.07, 'AvgSalary': 112000},
        {'Skill': 'Agile', 'Category': 'Methodology', 'Popularity': 85, 'GrowthRate': 0.06, 'AvgSalary': 115000},
        {'Skill': 'Scrum', 'Category': 'Methodology', 'Popularity': 80, 'GrowthRate': 0.05, 'AvgSalary': 110000},
        {'Skill': 'Communication', 'Category': 'Soft Skills', 'Popularity': 95, 'GrowthRate': 0.08, 'AvgSalary': 110000},
        {'Skill': 'Problem Solving', 'Category': 'Soft Skills', 'Popularity': 93, 'GrowthRate': 0.07, 'AvgSalary': 112000},
        {'Skill': 'Teamwork', 'Category': 'Soft Skills', 'Popularity': 92, 'GrowthRate': 0.06, 'AvgSalary': 108000}
    ]
    
    # Convert to DataFrame
    df = pd.DataFrame(skills_data)
    
    # Add Years Experience Needed and Job Count columns
    df['YearsExperienceNeeded'] = np.random.uniform(1, 7, size=len(df)).round(1)
    df['JobCount'] = np.random.randint(500, 10000, size=len(df))
    
    return df
