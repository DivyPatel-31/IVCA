import pandas as pd
from datetime import datetime
import json
import os
import database as db
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = db.Base

# Define User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    skills = Column(JSON)  # Store skills as JSON array
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# Define Job model
class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String)
    salary = Column(String)
    description = Column(Text)
    requirements = Column(Text)
    date_posted = Column(String)
    url = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    
# Define SavedJob model for user-saved jobs
class SavedJob(Base):
    __tablename__ = "saved_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    match_percentage = Column(Float)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User")
    job = relationship("Job")

# Functions for user management
def create_user(name, email, skills=None):
    """Create a new user with the given information"""
    session = db.get_db()
    
    # Check if user already exists
    existing_user = session.query(User).filter(User.email == email).first()
    if existing_user:
        return existing_user.id
    
    # Create new user
    user = User(
        name=name,
        email=email,
        skills=skills or []
    )
    
    session.add(user)
    session.commit()
    
    return user.id

def update_user_skills(user_id, skills):
    """Update the skills for a user"""
    session = db.get_db()
    
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    user.skills = skills
    user.updated_at = datetime.now()
    
    session.commit()
    
    return True

def get_user_by_email(email):
    """Get user information by email"""
    session = db.get_db()
    
    user = session.query(User).filter(User.email == email).first()
    
    if not user:
        return None
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "skills": user.skills or [],
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat()
    }

def get_user_by_id(user_id):
    """Get user information by ID"""
    session = db.get_db()
    
    user = session.query(User).filter(User.id == user_id).first()
    
    if not user:
        return None
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "skills": user.skills or [],
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat()
    }

def save_job_for_user(user_id, job_data, match_percentage, notes=None):
    """Save a job for a user"""
    session = db.get_db()
    
    # Check if user exists
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # Check if job already exists in database
    job = session.query(Job).filter(Job.job_id == job_data.get('id')).first()
    
    if not job:
        # Create new job entry
        job = Job(
            job_id=job_data.get('id'),
            title=job_data.get('title'),
            company=job_data.get('company'),
            location=job_data.get('location'),
            salary=job_data.get('salary'),
            description=job_data.get('description'),
            requirements=job_data.get('requirements'),
            date_posted=job_data.get('date_posted'),
            url=job_data.get('url')
        )
        session.add(job)
        session.flush()  # To get the job ID
    
    # Check if user already saved this job
    existing_saved_job = session.query(SavedJob).filter(
        SavedJob.user_id == user_id,
        SavedJob.job_id == job.id
    ).first()
    
    if existing_saved_job:
        # Update existing saved job
        existing_saved_job.match_percentage = match_percentage
        if notes:
            existing_saved_job.notes = notes
        saved_job_id = existing_saved_job.id
    else:
        # Create new saved job
        saved_job = SavedJob(
            user_id=user_id,
            job_id=job.id,
            match_percentage=match_percentage,
            notes=notes
        )
        session.add(saved_job)
        session.flush()
        saved_job_id = saved_job.id
    
    session.commit()
    
    return saved_job_id

def get_saved_jobs(user_id):
    """Get all jobs saved by a user"""
    session = db.get_db()
    
    saved_jobs = session.query(SavedJob, Job).join(
        Job, SavedJob.job_id == Job.id
    ).filter(
        SavedJob.user_id == user_id
    ).all()
    
    result = []
    for saved_job, job in saved_jobs:
        result.append({
            "saved_job_id": saved_job.id,
            "match_percentage": saved_job.match_percentage,
            "notes": saved_job.notes,
            "saved_at": saved_job.created_at.isoformat(),
            "job": {
                "id": job.job_id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "salary": job.salary,
                "description": job.description,
                "requirements": job.requirements,
                "date_posted": job.date_posted,
                "url": job.url
            }
        })
    
    return result

def delete_saved_job(user_id, saved_job_id):
    """Delete a saved job for a user"""
    session = db.get_db()
    
    saved_job = session.query(SavedJob).filter(
        SavedJob.id == saved_job_id,
        SavedJob.user_id == user_id
    ).first()
    
    if not saved_job:
        return False
    
    session.delete(saved_job)
    session.commit()
    
    return True