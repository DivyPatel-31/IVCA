import pandas as pd
import numpy as np
import io
import json
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
import tempfile
import os
from data_processing import clean_data, transform_data, get_data_summary
from visualization import create_visualization

# Global variable to store the data
data_store = {"data": None, "filtered_data": None}

# Create FastAPI app
app = FastAPI(
    title="DataViz PM Tool API",
    description="API for data visualization and analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include database API router
from database_api import router as db_router
app.include_router(db_router)

# Add documentation information
app.title = "DataViz PM Tool API"
app.description = """
Data Visualization and Analysis API for Product Managers and Technical Teams

This API allows for:
- Uploading and managing datasets
- Cleaning and transforming data
- Creating visualizations
- Saving and retrieving data from database
- Statistical analysis of data

For more information, visit the main application or contact your administrator.
"""
app.version = "1.0.0"

# Pydantic models for request validation
class TransformRequest(BaseModel):
    method: str

class CleanRequest(BaseModel):
    method: str

class VisualizationRequest(BaseModel):
    chart_type: str
    x_axis: Union[str, List[str]]
    y_axis: Optional[str] = None
    color_by: Optional[str] = None
    title: Optional[str] = None
    orientation: Optional[str] = "Vertical"
    color_scheme: Optional[str] = "Plotly"
    bins: Optional[int] = None
    filters: Optional[Dict[str, Any]] = None

# API routes
@app.get("/")
def read_root():
    return {"message": "Welcome to the DataViz PM Tool API"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a data file (CSV, Excel, or JSON)"""
    try:
        # Save uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.write(await file.read())
            temp_path = temp.name
        
        # Determine file type and load data
        file_extension = file.filename.split(".")[-1].lower()
        
        if file_extension == "csv":
            data = pd.read_csv(temp_path)
        elif file_extension in ["xlsx", "xls"]:
            data = pd.read_excel(temp_path)
        elif file_extension == "json":
            data = pd.read_json(temp_path)
        else:
            os.unlink(temp_path)
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        # Store the data
        data_store["data"] = data
        data_store["filtered_data"] = data.copy()
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "rows": len(data),
            "columns": len(data.columns)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

@app.get("/api/data")
def get_data(limit: int = 100, offset: int = 0):
    """Get the current dataset (with pagination)"""
    if data_store["filtered_data"] is None:
        raise HTTPException(status_code=404, detail="No data available. Please upload a file first.")
    
    data = data_store["filtered_data"]
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

@app.get("/api/data/summary")
def get_summary():
    """Get summary statistics for the dataset"""
    if data_store["filtered_data"] is None:
        raise HTTPException(status_code=404, detail="No data available. Please upload a file first.")
    
    summary = get_data_summary(data_store["filtered_data"])
    return summary

@app.post("/api/data/clean")
def clean_dataset(request: CleanRequest):
    """Clean the dataset using the specified method"""
    if data_store["data"] is None:
        raise HTTPException(status_code=404, detail="No data available. Please upload a file first.")
    
    try:
        data_store["filtered_data"] = clean_data(data_store["data"], request.method)
        return {"message": f"Data cleaned using method: {request.method}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clean data: {str(e)}")

@app.post("/api/data/transform")
def transform_dataset(request: TransformRequest):
    """Transform the dataset using the specified method"""
    if data_store["filtered_data"] is None:
        raise HTTPException(status_code=404, detail="No data available. Please upload a file first.")
    
    try:
        data_store["filtered_data"] = transform_data(data_store["filtered_data"], request.method)
        return {"message": f"Data transformed using method: {request.method}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transform data: {str(e)}")

@app.post("/api/visualize")
def create_visualization_api(request: VisualizationRequest):
    """Create a visualization based on the specified parameters"""
    if data_store["filtered_data"] is None:
        raise HTTPException(status_code=404, detail="No data available. Please upload a file first.")
    
    try:
        data = data_store["filtered_data"]
        
        # Apply filters if provided
        if request.filters:
            from visualization import apply_filters
            data = apply_filters(data, request.filters)
        
        # Create visualization
        fig = create_visualization(
            data,
            request.chart_type,
            request.x_axis,
            request.y_axis,
            request.color_by,
            request.title,
            request.orientation,
            request.color_scheme,
            request.bins
        )
        
        # Return HTML representation
        return {
            "message": "Visualization created successfully",
            "html": fig.to_html(include_plotlyjs="cdn", full_html=False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create visualization: {str(e)}")

@app.get("/api/columns")
def get_columns():
    """Get the list of columns in the dataset"""
    if data_store["filtered_data"] is None:
        raise HTTPException(status_code=404, detail="No data available. Please upload a file first.")
    
    data = data_store["filtered_data"]
    
    # Categorize columns by data type
    numeric_columns = data.select_dtypes(include=np.number).columns.tolist()
    categorical_columns = data.select_dtypes(include=['object']).columns.tolist()
    datetime_columns = data.select_dtypes(include=['datetime']).columns.tolist()
    
    return {
        "all_columns": data.columns.tolist(),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "datetime_columns": datetime_columns
    }

def start_api_server():
    """Start the FastAPI server"""
    uvicorn.run("api:app", host="0.0.0.0", port=8000, log_level="info")
