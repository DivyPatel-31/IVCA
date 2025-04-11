# DataViz PM Tool

A Streamlit-based data visualization and analysis tool for product managers with API integration capabilities for technical teams.

## Features

- Data upload and import (CSV, Excel, JSON)
- Data cleaning and preprocessing
- Interactive data visualization dashboard
- Creation of shareable visualizations
- Export functionality for reports and charts
- API endpoints for technical team integration
- Simple user interface for non-technical users

## Getting Started

### Prerequisites

- Python 3.7+
- Streamlit
- Pandas
- Plotly
- FastAPI
- NumPy
- scikit-learn

### Installation

1. Clone this repository
2. Install dependencies: `pip install streamlit pandas plotly fastapi uvicorn numpy scikit-learn`
3. Run the application: `streamlit run app.py`

## Usage

### Data Upload

1. Use the sidebar to upload your data file (CSV, Excel, or JSON)
2. The tool will automatically load and display basic information about your data

### Data Cleaning and Transformation

1. Choose cleaning options in the sidebar (remove missing values, fill with mean/mode, etc.)
2. Apply transformations to your data (normalization, log transform, one-hot encoding)

### Data Visualization

1. Select the "Visualization" tab
2. Choose a chart type (Bar Chart, Line Chart, Scatter Plot, etc.)
3. Configure the visualization by selecting columns for axes, colors, etc.
4. Generate and view your visualization
5. Download the visualization as HTML or image

### Reports

1. Select the "Reports & Sharing" tab
2. Configure report options
3. Generate and download reports

### API Integration

Technical teams can integrate with the application using the API endpoints:

- `/api/docs` - Interactive API documentation
- `/api/upload` - Upload data file
- `/api/data` - Get the current dataset
- `/api/data/summary` - Get dataset summary statistics
- `/api/visualize` - Generate a visualization

## Architecture

The application consists of the following components:

1. `app.py` - Main Streamlit application
2. `data_processing.py` - Data cleaning and transformation functions
3. `visualization.py` - Visualization creation functions
4. `api.py` - FastAPI endpoints for integration
5. `utils.py` - Utility functions for data analysis

## API Documentation

API documentation is available at http://localhost:8000/docs when the application is running.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
