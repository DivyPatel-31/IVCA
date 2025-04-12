import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
import streamlit as st

def format_large_number(num):
    """Format large numbers with commas"""
    return f"{num:,}"

def format_percentage(value):
    """Format number as percentage"""
    return f"{value:.2f}%"

def get_file_extension(filename):
    """Get the file extension from a filename"""
    return filename.split(".")[-1].lower()

def is_valid_file_extension(filename, allowed_extensions=["csv", "xlsx", "json"]):
    """Check if the file has a valid extension"""
    ext = get_file_extension(filename)
    return ext in allowed_extensions

def read_data_file(file_path):
    """Read data from a file based on its extension"""
    ext = get_file_extension(file_path)
    
    if ext == "csv":
        return pd.read_csv(file_path)
    elif ext == "xlsx":
        return pd.read_excel(file_path)
    elif ext == "json":
        return pd.read_json(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

def save_data_file(df, file_path):
    """Save data to a file based on its extension"""
    ext = get_file_extension(file_path)
    
    if ext == "csv":
        df.to_csv(file_path, index=False)
    elif ext == "xlsx":
        df.to_excel(file_path, index=False)
    elif ext == "json":
        df.to_json(file_path, orient="records")
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

def detect_date_columns(df):
    """Detect columns that contain dates and convert them"""
    date_columns = []
    
    for col in df.columns:
        # Skip if column is not object type
        if df[col].dtype != 'object':
            continue
        
        # Check if values look like dates
        try:
            # Try to parse the first non-null value
            sample = df[col].dropna().iloc[0]
            pd.to_datetime(sample)
            
            # If successful, convert the entire column
            df[col] = pd.to_datetime(df[col], errors='coerce')
            date_columns.append(col)
        except:
            pass
    
    return df, date_columns

def detect_numeric_columns(df):
    """Detect columns that could be numeric but are stored as strings"""
    numeric_columns = []
    
    for col in df.columns:
        # Skip if column is already numeric
        if pd.api.types.is_numeric_dtype(df[col]):
            continue
        
        # Check if values can be converted to numeric
        try:
            # Try to convert to numeric
            pd.to_numeric(df[col], errors='raise')
            
            # If successful, convert the entire column
            df[col] = pd.to_numeric(df[col])
            numeric_columns.append(col)
        except:
            pass
    
    return df, numeric_columns

def get_database_url():
    """Get the database URL from environment variable with fallback"""
    return os.environ.get('DATABASE_URL', 'sqlite:///ivca.db')

def load_user_data(user_id):
    """Load user data from database or file"""
    try:
        # Try to load from database if available
        from database import get_user_data
        return get_user_data(user_id)
    except ImportError:
        # Fall back to loading from JSON file
        user_file = f"data/users/{user_id}.json"
        if os.path.exists(user_file):
            with open(user_file, "r") as f:
                return json.load(f)
        return None

def save_user_data(user_id, user_data):
    """Save user data to database or file"""
    try:
        # Try to save to database if available
        from database import save_user_data
        return save_user_data(user_id, user_data)
    except ImportError:
        # Fall back to saving to JSON file
        # Create directory if it doesn't exist
        os.makedirs("data/users", exist_ok=True)
        
        user_file = f"data/users/{user_id}.json"
        with open(user_file, "w") as f:
            json.dump(user_data, f, indent=2)
        return True

def generate_id():
    """Generate a unique ID"""
    import uuid
    return str(uuid.uuid4())

def get_current_time():
    """Get current time as ISO 8601 string"""
    return datetime.now().isoformat()

def create_download_link(df, filename, text):
    """Create a download link for a DataFrame"""
    csv = df.to_csv(index=False)
    
    # Create download button
    st.download_button(
        label=text,
        data=csv,
        file_name=filename,
        mime='text/csv',
    )
