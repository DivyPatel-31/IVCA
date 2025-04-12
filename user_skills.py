import os
import json
import utils
from datetime import datetime

# Path for storing user data
USER_DATA_DIR = "data/users"
os.makedirs(USER_DATA_DIR, exist_ok=True)

# Try to use database if available
try:
    import database
    USE_DATABASE = True
except ImportError:
    USE_DATABASE = False

def get_user_data_path(user_id):
    """Get the path to a user's data file"""
    return os.path.join(USER_DATA_DIR, f"{user_id}.json")

def create_user(name, email, skills):
    """
    Create a new user with the given name, email, and skills
    
    Parameters:
    name (str): User name
    email (str): User email
    skills (list): List of user skills
    
    Returns:
    str: User ID
    """
    # Try to use database if available
    if USE_DATABASE:
        try:
            return database.create_user_db(name, email, skills)
        except Exception as e:
            print(f"Database error: {e}")
            # Fall back to file-based storage
    
    # Generate unique user ID
    user_id = utils.generate_id()
    
    # Create user data object
    user_data = {
        "id": user_id,
        "name": name,
        "email": email,
        "skills": skills,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "saved_jobs": []
    }
    
    # Save user data
    user_file = get_user_data_path(user_id)
    with open(user_file, "w") as f:
        json.dump(user_data, f, indent=2)
    
    return user_id

def get_user_by_id(user_id):
    """Get user data by ID"""
    # Try to use database if available
    if USE_DATABASE:
        try:
            return database.get_user_data(user_id)
        except Exception as e:
            print(f"Database error: {e}")
            # Fall back to file-based storage
            
    # Use file-based storage
    user_file = get_user_data_path(user_id)
    
    if not os.path.exists(user_file):
        return None
    
    with open(user_file, "r") as f:
        return json.load(f)

def get_user_by_email(email):
    """Get user data by email"""
    # Try to use database if available
    if USE_DATABASE:
        try:
            return database.get_user_by_email_db(email)
        except Exception as e:
            print(f"Database error: {e}")
            # Fall back to file-based storage
    
    # Check if users directory exists
    if not os.path.exists(USER_DATA_DIR):
        return None
    
    # Look through all user files
    for filename in os.listdir(USER_DATA_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(USER_DATA_DIR, filename)
            
            with open(file_path, "r") as f:
                user_data = json.load(f)
                
                if user_data.get("email") == email:
                    return user_data
    
    return None

def update_user_skills(user_id, skills):
    """Update a user's skills"""
    # Try to use database if available
    if USE_DATABASE:
        try:
            # Get current user data
            user_data = database.get_user_data(user_id)
            if not user_data:
                return False
                
            # Update and save user data
            user_data["skills"] = skills
            return database.save_user_data(user_id, user_data)
        except Exception as e:
            print(f"Database error: {e}")
            # Fall back to file-based storage
    
    # Use file-based storage
    user_data = get_user_by_id(user_id)
    
    if not user_data:
        return False
    
    # Update skills and updated_at timestamp
    user_data["skills"] = skills
    user_data["updated_at"] = datetime.now().isoformat()
    
    # Save updated user data
    user_file = get_user_data_path(user_id)
    with open(user_file, "w") as f:
        json.dump(user_data, f, indent=2)
    
    return True

def save_job_for_user(user_id, job_data, match_percentage):
    """Save a job to a user's saved jobs"""
    # Try to use database if available
    if USE_DATABASE:
        try:
            from database import SavedJob
            from utils import generate_id
            import sqlalchemy
            
            # Connect to database
            session = database.get_session()
            
            # Generate unique ID for saved job
            saved_job_id = generate_id()
            
            # Create new saved job record
            new_saved_job = SavedJob(
                id=saved_job_id,
                user_id=user_id,
                job_data=job_data,
                match_percentage=match_percentage,
                notes=""
            )
            
            try:
                session.add(new_saved_job)
                session.commit()
                return saved_job_id
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
                
        except Exception as e:
            print(f"Database error saving job: {e}")
            # Fall back to file-based storage
    
    # Use file-based storage
    user_data = get_user_by_id(user_id)
    
    if not user_data:
        return False
    
    # Generate unique saved job ID
    saved_job_id = utils.generate_id()
    
    # Create saved job entry
    saved_job = {
        "saved_job_id": saved_job_id,
        "job": job_data,
        "match_percentage": match_percentage,
        "saved_at": datetime.now().isoformat(),
        "notes": ""
    }
    
    # Add to saved jobs
    if "saved_jobs" not in user_data:
        user_data["saved_jobs"] = []
    
    user_data["saved_jobs"].append(saved_job)
    user_data["updated_at"] = datetime.now().isoformat()
    
    # Save updated user data
    user_file = get_user_data_path(user_id)
    with open(user_file, "w") as f:
        json.dump(user_data, f, indent=2)
    
    return saved_job_id

def get_saved_jobs(user_id):
    """Get all saved jobs for a user"""
    # Try to use database if available
    if USE_DATABASE:
        try:
            # Get user data with saved jobs
            user_data = database.get_user_data(user_id)
            
            if not user_data or "saved_jobs" not in user_data:
                return []
            
            return user_data["saved_jobs"]
        except Exception as e:
            print(f"Database error getting saved jobs: {e}")
            # Fall back to file-based storage
    
    # Use file-based storage
    user_data = get_user_by_id(user_id)
    
    if not user_data or "saved_jobs" not in user_data:
        return []
    
    return user_data["saved_jobs"]

def delete_saved_job(user_id, saved_job_id):
    """Delete a saved job from a user's saved jobs"""
    # Try to use database if available
    if USE_DATABASE:
        try:
            from database import SavedJob
            
            # Connect to database
            session = database.get_session()
            
            try:
                # Find and delete the saved job
                saved_job = session.query(SavedJob).filter_by(
                    id=saved_job_id, 
                    user_id=user_id
                ).first()
                
                if not saved_job:
                    return False
                
                session.delete(saved_job)
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
                
        except Exception as e:
            print(f"Database error deleting job: {e}")
            # Fall back to file-based storage
    
    # Use file-based storage
    user_data = get_user_by_id(user_id)
    
    if not user_data or "saved_jobs" not in user_data:
        return False
    
    # Find and remove the saved job
    initial_count = len(user_data["saved_jobs"])
    user_data["saved_jobs"] = [job for job in user_data["saved_jobs"] 
                               if job.get("saved_job_id") != saved_job_id]
    
    # Check if a job was removed
    if len(user_data["saved_jobs"]) == initial_count:
        return False
    
    # Update timestamp
    user_data["updated_at"] = datetime.now().isoformat()
    
    # Save updated user data
    user_file = get_user_data_path(user_id)
    with open(user_file, "w") as f:
        json.dump(user_data, f, indent=2)
    
    return True
