import os
import json
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Define base class for SQLAlchemy models
Base = declarative_base()

# Define database models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    skills = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    saved_jobs = relationship("SavedJob", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(name='{self.name}', email='{self.email}')>"

class SavedJob(Base):
    __tablename__ = 'saved_jobs'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    job_data = Column(JSON, nullable=False)
    match_percentage = Column(Float)
    saved_at = Column(DateTime, default=datetime.now)
    notes = Column(Text)
    
    user = relationship("User", back_populates="saved_jobs")
    
    def __repr__(self):
        return f"<SavedJob(id='{self.id}', user_id='{self.user_id}')>"

class Dataset(Base):
    __tablename__ = 'datasets'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    file_type = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    data_path = Column(String)  # Path to saved data file
    
    def __repr__(self):
        return f"<Dataset(name='{self.name}')>"

class SkillAssessment(Base):
    __tablename__ = 'skill_assessments'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    target_job = Column(String)
    assessment_data = Column(JSON, nullable=False)  # Stores the complete skill assessment
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<SkillAssessment(user_id='{self.user_id}', target_job='{self.target_job}')>"

class Resume(Base):
    __tablename__ = 'resumes'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    filename = Column(String, nullable=False)
    extracted_data = Column(JSON, nullable=False)  # Stores extracted information
    improvement_suggestions = Column(JSON)  # Stores improvement suggestions
    uploaded_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Resume(id='{self.id}', user_id='{self.user_id}', filename='{self.filename}')"

# Database setup and connection functions
def get_engine(db_url=None):
    """Get SQLAlchemy engine"""
    if db_url is None:
        db_url = os.environ.get('DATABASE_URL', 'sqlite:///ivca.db')
        
        # Handle special case for SQLite to ensure the data directory exists
        if db_url.startswith('sqlite:///'):
            db_path = db_url.replace('sqlite:///', '')
            os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
            
    return create_engine(db_url)

def init_db():
    """Initialize the database by creating all tables"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """Get a session for database operations"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

# User-related functions
def create_user_db(name, email, skills):
    """Create a new user in the database"""
    from utils import generate_id
    
    session = get_session()
    
    # Check if user with this email already exists
    existing_user = session.query(User).filter_by(email=email).first()
    if existing_user:
        session.close()
        return existing_user.id
    
    # Generate a new ID
    user_id = generate_id()
    
    # Create new user
    new_user = User(
        id=user_id,
        name=name,
        email=email,
        skills=skills
    )
    
    try:
        session.add(new_user)
        session.commit()
        return user_id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_user_data(user_id):
    """Get user data by ID"""
    session = get_session()
    
    try:
        user = session.query(User).filter_by(id=user_id).first()
        
        if user:
            # Convert SQLAlchemy model to dictionary
            user_dict = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "skills": user.skills,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
                "saved_jobs": []
            }
            
            # Add saved jobs
            for job in user.saved_jobs:
                job_dict = {
                    "saved_job_id": job.id,
                    "job": job.job_data,
                    "match_percentage": job.match_percentage,
                    "saved_at": job.saved_at.isoformat(),
                    "notes": job.notes
                }
                user_dict["saved_jobs"].append(job_dict)
                
            return user_dict
        
        return None
    finally:
        session.close()

def save_user_data(user_id, user_data):
    """Update user data"""
    session = get_session()
    
    try:
        user = session.query(User).filter_by(id=user_id).first()
        
        if not user:
            return False
        
        # Update user fields
        if "name" in user_data:
            user.name = user_data["name"]
        if "email" in user_data:
            user.email = user_data["email"]
        if "skills" in user_data:
            user.skills = user_data["skills"]
        
        # Update saved jobs if provided
        if "saved_jobs" in user_data:
            # Clear existing saved jobs and add new ones
            for job in user.saved_jobs:
                session.delete(job)
            
            # Add updated saved jobs
            from utils import generate_id
            
            for job_data in user_data["saved_jobs"]:
                saved_job = SavedJob(
                    id=job_data.get("saved_job_id", generate_id()),
                    user_id=user_id,
                    job_data=job_data.get("job", {}),
                    match_percentage=job_data.get("match_percentage"),
                    saved_at=datetime.fromisoformat(job_data.get("saved_at", datetime.now().isoformat())),
                    notes=job_data.get("notes", "")
                )
                session.add(saved_job)
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_user_by_email_db(email):
    """Get user by email"""
    session = get_session()
    
    try:
        user = session.query(User).filter_by(email=email).first()
        
        if user:
            return get_user_data(user.id)
        
        return None
    finally:
        session.close()

# Dataset-related functions
def save_dataset(name, description, df, file_type):
    """Save a dataset to the database"""
    from utils import generate_id
    
    session = get_session()
    
    # Generate an ID for the dataset
    dataset_id = generate_id()
    
    # Create data directory if it doesn't exist
    data_dir = "data/datasets"
    os.makedirs(data_dir, exist_ok=True)
    
    # Save data to file
    data_path = f"{data_dir}/{dataset_id}.{file_type}"
    
    if file_type == "csv":
        df.to_csv(data_path, index=False)
    elif file_type == "xlsx":
        df.to_excel(data_path, index=False)
    elif file_type == "json":
        df.to_json(data_path, orient="records")
    
    # Create dataset record
    dataset = Dataset(
        id=dataset_id,
        name=name,
        description=description,
        file_type=file_type,
        data_path=data_path
    )
    
    try:
        session.add(dataset)
        session.commit()
        return dataset_id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_dataset(dataset_id):
    """Get a dataset by ID"""
    session = get_session()
    
    try:
        dataset = session.query(Dataset).filter_by(id=dataset_id).first()
        
        if dataset:
            from utils import read_data_file
            
            # Load the data from file
            df = read_data_file(dataset.data_path)
            
            return {
                "id": dataset.id,
                "name": dataset.name,
                "description": dataset.description,
                "file_type": dataset.file_type,
                "created_at": dataset.created_at.isoformat(),
                "dataframe": df
            }
        
        return None
    finally:
        session.close()

def save_skill_assessment(user_id, target_job, assessment_data):
    """Save a skill assessment to the database"""
    from utils import generate_id
    
    session = get_session()
    
    # Generate an ID for the assessment
    assessment_id = generate_id()
    
    # Create skill assessment record
    assessment = SkillAssessment(
        id=assessment_id,
        user_id=user_id,
        target_job=target_job,
        assessment_data=assessment_data
    )
    
    try:
        session.add(assessment)
        session.commit()
        return assessment_id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_skill_assessment(user_id, assessment_id=None):
    """Get skill assessments for a user"""
    session = get_session()
    
    try:
        if assessment_id:
            # Get specific assessment
            assessment = session.query(SkillAssessment).filter_by(id=assessment_id, user_id=user_id).first()
            
            if assessment:
                return {
                    "id": assessment.id,
                    "user_id": assessment.user_id,
                    "target_job": assessment.target_job,
                    "assessment_data": assessment.assessment_data,
                    "created_at": assessment.created_at.isoformat()
                }
            
            return None
        else:
            # Get all assessments for user
            assessments = session.query(SkillAssessment).filter_by(user_id=user_id).all()
            
            return [{
                "id": assessment.id,
                "user_id": assessment.user_id,
                "target_job": assessment.target_job,
                "assessment_data": assessment.assessment_data,
                "created_at": assessment.created_at.isoformat()
            } for assessment in assessments]
    finally:
        session.close()

# Initialize the database when this module is imported
init_db()