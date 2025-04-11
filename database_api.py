from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import database as db
import pandas as pd
import json
from datetime import datetime

# Create router
router = APIRouter(
    prefix="/api/db",
    tags=["database"],
    responses={404: {"description": "Not found"}},
)

# Pydantic models for request/response validation
class DatasetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    file_type: str

class DatasetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    file_type: str
    created_at: datetime
    updated_at: datetime
    column_names: List[str]
    row_count: int

class VisualizationCreate(BaseModel):
    dataset_id: int
    name: str
    description: Optional[str] = None
    chart_type: str
    config: Dict[str, Any]

class VisualizationResponse(BaseModel):
    id: int
    dataset_id: int
    name: str
    description: Optional[str] = None
    chart_type: str
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class ProcessingStepCreate(BaseModel):
    dataset_id: int
    processing_steps: List[Dict[str, Any]]

# API Routes
@router.get("/datasets", response_model=List[DatasetResponse])
def get_datasets():
    """Get all datasets"""
    datasets = db.get_all_datasets()
    return [
        DatasetResponse(
            id=d.id,
            name=d.name,
            description=d.description,
            file_type=d.file_type,
            created_at=d.created_at,
            updated_at=d.updated_at,
            column_names=json.loads(d.column_names),
            row_count=d.row_count
        ) for d in datasets
    ]

@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: int):
    """Get dataset by ID"""
    dataset = db.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    return DatasetResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        file_type=dataset.file_type,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at,
        column_names=json.loads(dataset.column_names),
        row_count=dataset.row_count
    )

@router.get("/datasets/{dataset_id}/data")
def get_dataset_data(dataset_id: int, processed: bool = False, limit: int = 1000, offset: int = 0):
    """Get dataset data with pagination"""
    dataset = db.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    data = db.get_dataset_data(dataset_id, processed)
    if data is None:
        raise HTTPException(status_code=404, detail="Dataset data not found")
        
    total_rows = len(data)
    if offset >= total_rows:
        return {"data": [], "total": total_rows, "offset": offset, "limit": limit}
        
    end_idx = min(offset + limit, total_rows)
    data_slice = data.iloc[offset:end_idx]
    
    # Convert to JSON-serializable format
    json_data = json.loads(data_slice.to_json(orient="records"))
    
    return {
        "data": json_data,
        "total": total_rows,
        "offset": offset,
        "limit": limit
    }

@router.delete("/datasets/{dataset_id}")
def delete_dataset(dataset_id: int):
    """Delete dataset and all associated data"""
    dataset = db.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    success = db.delete_dataset(dataset_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete dataset")
        
    return {"message": "Dataset deleted successfully"}

@router.get("/visualizations", response_model=List[VisualizationResponse])
def get_visualizations():
    """Get all visualizations"""
    visualizations = db.get_all_visualizations()
    return [
        VisualizationResponse(
            id=v.id,
            dataset_id=v.dataset_id,
            name=v.name,
            description=v.description,
            chart_type=v.chart_type,
            config=json.loads(v.config),
            created_at=v.created_at,
            updated_at=v.updated_at
        ) for v in visualizations
    ]

@router.get("/datasets/{dataset_id}/visualizations", response_model=List[VisualizationResponse])
def get_dataset_visualizations(dataset_id: int):
    """Get all visualizations for a dataset"""
    dataset = db.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    visualizations = db.get_dataset_visualizations(dataset_id)
    return [
        VisualizationResponse(
            id=v.id,
            dataset_id=v.dataset_id,
            name=v.name,
            description=v.description,
            chart_type=v.chart_type,
            config=json.loads(v.config),
            created_at=v.created_at,
            updated_at=v.updated_at
        ) for v in visualizations
    ]

@router.get("/visualizations/{viz_id}", response_model=VisualizationResponse)
def get_visualization(viz_id: int):
    """Get visualization by ID"""
    viz = db.get_visualization(viz_id)
    if not viz:
        raise HTTPException(status_code=404, detail="Visualization not found")
        
    return VisualizationResponse(
        id=viz.id,
        dataset_id=viz.dataset_id,
        name=viz.name,
        description=viz.description,
        chart_type=viz.chart_type,
        config=json.loads(viz.config),
        created_at=viz.created_at,
        updated_at=viz.updated_at
    )

@router.post("/visualizations", response_model=VisualizationResponse)
def create_visualization(viz_create: VisualizationCreate):
    """Create a new visualization"""
    dataset = db.get_dataset(viz_create.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    try:
        viz_id = db.save_visualization(
            viz_create.dataset_id,
            viz_create.name,
            viz_create.description,
            viz_create.chart_type,
            viz_create.config
        )
        
        viz = db.get_visualization(viz_id)
        
        return VisualizationResponse(
            id=viz.id,
            dataset_id=viz.dataset_id,
            name=viz.name,
            description=viz.description,
            chart_type=viz.chart_type,
            config=json.loads(viz.config),
            created_at=viz.created_at,
            updated_at=viz.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create visualization: {str(e)}")

@router.delete("/visualizations/{viz_id}")
def delete_visualization(viz_id: int):
    """Delete visualization"""
    viz = db.get_visualization(viz_id)
    if not viz:
        raise HTTPException(status_code=404, detail="Visualization not found")
        
    success = db.delete_visualization(viz_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete visualization")
        
    return {"message": "Visualization deleted successfully"}

@router.post("/datasets/{dataset_id}/process", response_model=dict)
def process_dataset_data(dataset_id: int, processing: ProcessingStepCreate):
    """Process dataset data and save the result"""
    dataset = db.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    # Get the original data
    data = db.get_dataset_data(dataset_id, processed=False)
    if data is None:
        raise HTTPException(status_code=404, detail="Dataset data not found")
    
    # Apply processing steps
    processed_data = data.copy()
    processing_log = []
    
    for step in processing.processing_steps:
        step_type = step.get("type")
        step_params = step.get("params", {})
        
        try:
            if step_type == "clean":
                method = step_params.get("method", "drop_rows")
                from data_processing import clean_data
                processed_data = clean_data(processed_data, method)
                processing_log.append({"type": "clean", "method": method, "success": True})
                
            elif step_type == "transform":
                method = step_params.get("method", "none")
                from data_processing import transform_data
                processed_data = transform_data(processed_data, method)
                processing_log.append({"type": "transform", "method": method, "success": True})
                
            else:
                processing_log.append({"type": step_type, "error": "Unknown step type", "success": False})
                
        except Exception as e:
            processing_log.append({"type": step_type, "error": str(e), "success": False})
    
    # Save the processed data
    try:
        saved_data_id = db.save_processed_data(dataset_id, processed_data, processing_log)
        return {
            "message": "Data processed successfully",
            "dataset_id": dataset_id,
            "saved_data_id": saved_data_id,
            "row_count": len(processed_data),
            "processing_log": processing_log
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save processed data: {str(e)}")