from fastapi import APIRouter, HTTPException, Body, Depends, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import database

router = APIRouter(
    prefix="/api/database",
    tags=["database"],
)

# Models for request/response
class UserBase(BaseModel):
    name: str
    email: str
    skills: List[str]

class UserResponse(UserBase):
    id: str
    created_at: str
    updated_at: str
    
class SavedJobBase(BaseModel):
    job_data: Dict[str, Any]
    match_percentage: float
    notes: Optional[str] = None

class SavedJobResponse(SavedJobBase):
    saved_job_id: str
    saved_at: str
    
class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None
    file_type: str

class DatasetResponse(DatasetBase):
    id: str
    created_at: str
    
class SkillAssessmentBase(BaseModel):
    target_job: str
    assessment_data: Dict[str, Any]

class SkillAssessmentResponse(SkillAssessmentBase):
    id: str
    user_id: str
    created_at: str

# API key authentication (simple version)
def get_api_key(api_key: str = Query(..., alias="api_key")):
    import os
    if api_key != os.environ.get("API_KEY", "default_key"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

# User endpoints
@router.post("/users", response_model=Dict[str, str])
async def create_user(
    user_data: UserBase,
    api_key: str = Depends(get_api_key)
):
    """Create a new user"""
    try:
        user_id = database.create_user_db(
            name=user_data.name,
            email=user_data.email,
            skills=user_data.skills
        )
        return {"user_id": user_id, "message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@router.get("/users/{user_id}", response_model=Dict[str, Any])
async def get_user(
    user_id: str,
    api_key: str = Depends(get_api_key)
):
    """Get user data by ID"""
    user_data = database.get_user_data(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return user_data

@router.put("/users/{user_id}", response_model=Dict[str, str])
async def update_user(
    user_id: str,
    user_data: Dict[str, Any] = Body(...),
    api_key: str = Depends(get_api_key)
):
    """Update user data"""
    success = database.save_user_data(user_id, user_data)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully"}

@router.get("/users/email/{email}", response_model=Dict[str, Any])
async def get_user_by_email(
    email: str,
    api_key: str = Depends(get_api_key)
):
    """Get user by email"""
    user_data = database.get_user_by_email_db(email)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return user_data

# Dataset endpoints
@router.post("/datasets", response_model=Dict[str, str])
async def create_dataset(
    dataset_data: DatasetBase,
    data: List[Dict[str, Any]] = Body(...),
    api_key: str = Depends(get_api_key)
):
    """Save a dataset"""
    import pandas as pd
    
    try:
        # Convert data to DataFrame
        df = pd.DataFrame(data)
        
        # Save dataset
        dataset_id = database.save_dataset(
            name=dataset_data.name,
            description=dataset_data.description,
            df=df,
            file_type=dataset_data.file_type
        )
        
        return {"dataset_id": dataset_id, "message": "Dataset saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving dataset: {str(e)}")

@router.get("/datasets/{dataset_id}", response_model=Dict[str, Any])
async def get_dataset(
    dataset_id: str,
    api_key: str = Depends(get_api_key)
):
    """Get dataset by ID"""
    dataset = database.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Convert DataFrame to records for JSON response
    dataset["data"] = dataset["dataframe"].to_dict(orient="records")
    del dataset["dataframe"]
    
    return dataset

# Skill assessment endpoints
@router.post("/skill-assessments/{user_id}", response_model=Dict[str, str])
async def create_skill_assessment(
    user_id: str,
    assessment_data: SkillAssessmentBase,
    api_key: str = Depends(get_api_key)
):
    """Save a skill assessment"""
    try:
        assessment_id = database.save_skill_assessment(
            user_id=user_id,
            target_job=assessment_data.target_job,
            assessment_data=assessment_data.assessment_data
        )
        
        return {"assessment_id": assessment_id, "message": "Skill assessment saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving skill assessment: {str(e)}")

@router.get("/skill-assessments/{user_id}", response_model=List[Dict[str, Any]])
async def get_user_skill_assessments(
    user_id: str,
    api_key: str = Depends(get_api_key)
):
    """Get all skill assessments for a user"""
    assessments = database.get_skill_assessment(user_id)
    return assessments

@router.get("/skill-assessments/{user_id}/{assessment_id}", response_model=Dict[str, Any])
async def get_skill_assessment_by_id(
    user_id: str,
    assessment_id: str,
    api_key: str = Depends(get_api_key)
):
    """Get a specific skill assessment"""
    assessment = database.get_skill_assessment(user_id, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Skill assessment not found")
    return assessment