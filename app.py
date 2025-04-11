import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
import uvicorn
import threading
import time
import os
from data_processing import clean_data, transform_data
from visualization import create_visualization, apply_filters
from api import start_api_server
import utils
import database as db
import job_scraper
import user_skills
from job_matcher import render_job_matcher_ui

# Set page config
st.set_page_config(
    page_title="IVCA",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'data' not in st.session_state:
    st.session_state.data = None
if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = None
if 'api_started' not in st.session_state:
    st.session_state.api_started = False
if 'chart_configs' not in st.session_state:
    st.session_state.chart_configs = {}
if 'generated_charts' not in st.session_state:
    st.session_state.generated_charts = []
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'processing_steps' not in st.session_state:
    st.session_state.processing_steps = []
if 'current_dataset_id' not in st.session_state:
    st.session_state.current_dataset_id = None
    
# User session state for job matcher
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
    
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
    
if 'user_skills' not in st.session_state:
    st.session_state.user_skills = []
    
if 'job_results' not in st.session_state:
    st.session_state.job_results = []

# Start the API server in a separate thread
if not st.session_state.api_started:
    threading.Thread(target=start_api_server, daemon=True).start()
    st.session_state.api_started = True
    # Give the API server a moment to start
    time.sleep(1)

# Custom CSS to adjust logo position
st.markdown("""
<style>
    .logo-container {
        text-align: left;
        padding: 0;
        margin-top: -20px;
        margin-bottom: -40px;
        margin-left: -25px;
    }
    .main-title {
        margin-top: -25px;
    }
</style>
""", unsafe_allow_html=True)

# Logo displayed on its own, larger and positioned toward top left
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
try:
    st.image("ivca_logo_circular.png", width=220)
except Exception as e:
    st.markdown("### 🔍")
    st.warning(f"Logo not found: {e}")
st.markdown('</div>', unsafe_allow_html=True)

# Title and description in main area
st.markdown('<div class="main-title">', unsafe_allow_html=True)
st.title("IVCA - Intelligent Visualization and Career Analysis")
st.markdown("""
This tool helps professionals analyze data and create shareable visualizations. 
Choose from our pre-loaded datasets for analysis and generate interactive visualizations.
Technical teams can also integrate with the API endpoints provided.

**NEW FEATURE**: Use the Career Matcher to find relevant job opportunities based on your skills. 
Simply enter your skills, and our tool will match you with suitable job positions.
""")
st.markdown('</div>', unsafe_allow_html=True)

# Import sample data module
import sample_data

# Sidebar for data loading and processing
with st.sidebar:
    st.header("Data Management")
    
    # Data source selection
    st.subheader("Sample Datasets")
    
    # Get sample datasets
    sample_datasets = sample_data.get_sample_datasets()
    dataset_names = list(sample_datasets.keys())
    
    selected_dataset = st.selectbox("Choose a dataset", dataset_names)
    
    if st.button("Load Dataset"):
        if selected_dataset in sample_datasets:
            # Load the selected dataset
            data = sample_datasets[selected_dataset]
            st.session_state.data = data
            st.session_state.filtered_data = data.copy()
            st.session_state.current_file = f"{selected_dataset}.csv"
            st.success(f"Successfully loaded {selected_dataset} with {len(data)} rows and {len(data.columns)} columns.")
            
            # Display dataset description based on which one was selected
            if selected_dataset == "Sales Data":
                st.markdown("""
                **Sales Data Description**:
                This dataset contains sales information from the past year, including:
                - Daily sales transactions
                - Product categories
                - Regional performance
                - Discount analysis
                """)
            elif selected_dataset == "Customer Analytics":
                st.markdown("""
                **Customer Analytics Description**:
                This dataset contains customer information, including:
                - Demographics (age, gender)
                - Purchase history
                - Subscription status
                - Customer lifetime value metrics
                """)
            elif selected_dataset == "HR Data":
                st.markdown("""
                **HR Data Description**:
                This dataset contains employee information, including:
                - Department and job level
                - Salary and experience details
                - Performance ratings
                - Training and promotion metrics
                """)
    
    # Advanced option to load from database if needed
    with st.expander("Advanced: Load from Database", expanded=False):
        try:
            datasets = db.get_all_datasets()
            if datasets:
                dataset_options = {f"{d.id}: {d.name} ({d.row_count} rows, {d.created_at.strftime('%Y-%m-%d')})": d.id for d in datasets}
                selected_db_dataset = st.selectbox("Select dataset from DB", list(dataset_options.keys()))
                dataset_id = dataset_options[selected_db_dataset]
                
                if st.button("Load Database Dataset"):
                    try:
                        # Get original or processed data
                        use_processed = st.checkbox("Use processed version (if available)")
                        data = db.get_dataset_data(dataset_id, processed=use_processed)
                        
                        if data is not None:
                            st.session_state.data = data
                            st.session_state.filtered_data = data.copy()
                            st.session_state.current_dataset_id = dataset_id
                            st.success(f"Successfully loaded database dataset with {len(data)} rows and {len(data.columns)} columns.")
                        else:
                            st.error("No data found for this dataset.")
                    except Exception as e:
                        st.error(f"Error loading dataset: {e}")
            else:
                st.info("No datasets found in the database.")
        except Exception as e:
            st.error(f"Error connecting to database: {e}")
    
    # Data cleaning options
    if st.session_state.data is not None:
        st.subheader("Data Cleaning")
        
        if st.checkbox("Remove missing values"):
            drop_method = st.radio("Method", ["Drop rows", "Fill with mean/mode", "Fill with zeros"])
            if st.button("Apply cleaning"):
                st.session_state.filtered_data = clean_data(
                    st.session_state.data, 
                    drop_method.lower().replace(" ", "_")
                )
                # Track processing steps for database
                st.session_state.processing_steps.append({
                    "type": "clean",
                    "method": drop_method.lower().replace(" ", "_"),
                    "timestamp": pd.Timestamp.now().isoformat()
                })
                st.success("Data cleaned successfully!")
        
        # Data transformation options
        st.subheader("Data Transformation")
        transform_option = st.selectbox(
            "Transform data", 
            ["None", "Normalize numeric columns", "Log transform", "One-hot encode categorical"]
        )
        
        if transform_option != "None" and st.button("Apply transformation"):
            st.session_state.filtered_data = transform_data(
                st.session_state.filtered_data,
                transform_option.lower().replace(" ", "_")
            )
            # Track processing steps for database
            st.session_state.processing_steps.append({
                "type": "transform",
                "method": transform_option.lower().replace(" ", "_"),
                "timestamp": pd.Timestamp.now().isoformat()
            })
            st.success("Data transformed successfully!")

# Main content area for data display and visualization
tab1, tab2, tab3, tab4, tab5 = st.tabs(["IVCA Explorer", "Visualization Studio", "Reports & Analytics", "API Integration", "Career Matcher"])

# Define a function to save the user's job search
def save_job_search(user_id, job_data):
    try:
        match_percentage = job_data.get('skills_match', 0)
        saved_job_id = user_skills.save_job_for_user(
            user_id,
            job_data,
            match_percentage
        )
        return saved_job_id
    except Exception as e:
        st.error(f"Error saving job: {e}")
        return None

with tab1:
    st.header("IVCA Explorer")
    
    if st.session_state.filtered_data is not None:
        data = st.session_state.filtered_data
        
        # Display basic data info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", len(data))
        with col2:
            st.metric("Columns", len(data.columns))
        with col3:
            missing_percentage = (data.isna().sum().sum() / (data.shape[0] * data.shape[1])) * 100
            st.metric("Missing values", f"{missing_percentage:.2f}%")
        
        # Column selector and data preview
        columns_to_view = st.multiselect(
            "Select columns to view",
            options=data.columns.tolist(),
            default=data.columns.tolist()[:5] if len(data.columns) > 5 else data.columns.tolist()
        )
        
        if columns_to_view:
            st.dataframe(data[columns_to_view].head(100))
        
        # Data statistics
        with st.expander("View data statistics"):
            st.write("Numerical columns statistics:")
            st.dataframe(data.describe())
            
            categorical_cols = data.select_dtypes(include=['object']).columns
            if not categorical_cols.empty:
                st.write("Categorical columns statistics:")
                for col in categorical_cols:
                    st.write(f"**{col}** - Unique values: {data[col].nunique()}")
                    st.dataframe(data[col].value_counts().head(10))

with tab2:
    st.header("Visualization Studio")
    
    if st.session_state.filtered_data is not None:
        data = st.session_state.filtered_data
        
        # Visualization configuration
        st.subheader("Create new visualization")
        
        # Chart type selector
        chart_type = st.selectbox(
            "Select chart type",
            ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram", "Box Plot", "Pie Chart", "Heatmap"]
        )
        
        # Column selectors based on chart type
        col1, col2 = st.columns(2)
        
        with col1:
            if chart_type in ["Bar Chart", "Line Chart", "Box Plot"]:
                x_axis = st.selectbox("X-axis", options=data.columns.tolist())
                y_axis = st.selectbox("Y-axis", options=[col for col in data.columns if pd.api.types.is_numeric_dtype(data[col])])
                color_by = st.selectbox("Color by (optional)", options=["None"] + data.columns.tolist())
                color_by = None if color_by == "None" else color_by
                
            elif chart_type == "Scatter Plot":
                x_axis = st.selectbox("X-axis", options=[col for col in data.columns if pd.api.types.is_numeric_dtype(data[col])])
                y_axis = st.selectbox("Y-axis", options=[col for col in data.columns if pd.api.types.is_numeric_dtype(data[col]) and col != x_axis])
                color_by = st.selectbox("Color by (optional)", options=["None"] + data.columns.tolist())
                color_by = None if color_by == "None" else color_by
                
            elif chart_type == "Histogram":
                x_axis = st.selectbox("Column", options=[col for col in data.columns if pd.api.types.is_numeric_dtype(data[col])])
                bins = st.slider("Number of bins", min_value=5, max_value=100, value=20)
                y_axis = None
                color_by = None
                
            elif chart_type == "Pie Chart":
                x_axis = st.selectbox("Categories", options=data.columns.tolist())
                y_axis = st.selectbox("Values", options=[col for col in data.columns if pd.api.types.is_numeric_dtype(data[col])])
                color_by = None
                
            elif chart_type == "Heatmap":
                numeric_cols = [col for col in data.columns if pd.api.types.is_numeric_dtype(data[col])]
                selected_cols = st.multiselect("Select columns for correlation", options=numeric_cols, default=numeric_cols[:min(5, len(numeric_cols))])
                x_axis = selected_cols
                y_axis = None
                color_by = None
        
        with col2:
            # Additional chart settings
            title = st.text_input("Chart title", f"{chart_type} of {x_axis if isinstance(x_axis, str) else 'selected columns'}")
            
            if chart_type in ["Bar Chart", "Line Chart", "Scatter Plot"]:
                orientation = st.radio("Orientation", ["Vertical", "Horizontal"])
            else:
                orientation = "Vertical"
                
            # Color scheme
            color_scheme = st.selectbox("Color scheme", ["Plotly", "Viridis", "Plasma", "Inferno", "Magma", "Cividis"])
            
            # Filter options
            with st.expander("Add filters"):
                filters = {}
                for column in data.columns:
                    if pd.api.types.is_numeric_dtype(data[column]):
                        min_val, max_val = float(data[column].min()), float(data[column].max())
                        filters[column] = st.slider(
                            f"Filter by {column}", 
                            min_value=min_val,
                            max_value=max_val,
                            value=(min_val, max_val)
                        )
                    elif pd.api.types.is_object_dtype(data[column]) and data[column].nunique() < 50:
                        unique_values = data[column].dropna().unique().tolist()
                        filters[column] = st.multiselect(
                            f"Filter by {column}",
                            options=unique_values,
                            default=unique_values
                        )
        
        # Apply filters to the data
        filtered_viz_data = apply_filters(data, filters)
        
        # Create and display visualization
        if st.button("Generate Visualization"):
            try:
                fig = create_visualization(
                    filtered_viz_data, 
                    chart_type, 
                    x_axis, 
                    y_axis, 
                    color_by, 
                    title, 
                    orientation, 
                    color_scheme,
                    bins if chart_type == "Histogram" else None
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Save chart configuration
                chart_config = {
                    "type": chart_type,
                    "x_axis": x_axis,
                    "y_axis": y_axis,
                    "color_by": color_by,
                    "title": title,
                    "orientation": orientation,
                    "color_scheme": color_scheme,
                    "filters": filters,
                    "bins": bins if chart_type == "Histogram" else None
                }
                
                # Add to generated charts
                if chart_config not in st.session_state.generated_charts:
                    st.session_state.generated_charts.append(chart_config)
                    
                # Export options
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button(
                        "Download as HTML",
                        io.StringIO(fig.to_html()).getvalue(),
                        file_name=f"{title.replace(' ', '_')}.html",
                        mime="text/html"
                    )
                with col2:
                    st.download_button(
                        "Download as Image",
                        fig.to_image(format="png"),
                        file_name=f"{title.replace(' ', '_')}.png",
                        mime="image/png"
                    )
                with col3:
                    if st.button("Save to Database"):
                        if 'current_dataset_id' in st.session_state and st.session_state.current_dataset_id:
                            # If we have a current dataset, save visualization to it
                            dataset_id = st.session_state.current_dataset_id
                        else:
                            # Otherwise, first save the dataset
                            try:
                                file_type = "csv"  # Default
                                if 'current_file' in st.session_state and st.session_state.current_file:
                                    file_type = st.session_state.current_file.split('.')[-1]
                                
                                dataset_id = db.save_dataset(
                                    f"Dataset for {title}",
                                    "Dataset for visualization",
                                    data,
                                    file_type
                                )
                                st.session_state.current_dataset_id = dataset_id
                            except Exception as e:
                                st.error(f"Error saving dataset: {e}")
                                dataset_id = None
                        
                        # Save visualization
                        if dataset_id:
                            try:
                                viz_id = db.save_visualization(
                                    dataset_id,
                                    title,
                                    f"Visualization of type {chart_type}",
                                    chart_type,
                                    chart_config
                                )
                                st.success(f"Visualization saved to database with ID: {viz_id}")
                            except Exception as e:
                                st.error(f"Error saving visualization: {e}")
                    
            except Exception as e:
                st.error(f"Error generating visualization: {e}")
        
        # Display saved visualizations
        if st.session_state.generated_charts:
            st.subheader("Saved Visualizations")
            
            for i, chart_config in enumerate(st.session_state.generated_charts):
                with st.expander(f"{chart_config['title']} ({chart_config['type']})"):
                    try:
                        filtered_data_for_viz = apply_filters(data, chart_config['filters'])
                        fig = create_visualization(
                            filtered_data_for_viz,
                            chart_config['type'],
                            chart_config['x_axis'],
                            chart_config['y_axis'],
                            chart_config['color_by'],
                            chart_config['title'],
                            chart_config['orientation'],
                            chart_config['color_scheme'],
                            chart_config.get('bins')
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.download_button(
                                "Download as HTML",
                                io.StringIO(fig.to_html()).getvalue(),
                                file_name=f"{chart_config['title'].replace(' ', '_')}.html",
                                mime="text/html",
                                key=f"html_{i}"
                            )
                        with col2:
                            st.download_button(
                                "Download as Image",
                                fig.to_image(format="png"),
                                file_name=f"{chart_config['title'].replace(' ', '_')}.png",
                                mime="image/png",
                                key=f"png_{i}"
                            )
                        with col3:
                            if st.button("Remove", key=f"remove_{i}"):
                                st.session_state.generated_charts.pop(i)
                                st.rerun()
                    except Exception as e:
                        st.error(f"Error regenerating visualization: {e}")

with tab3:
    st.header("Reports & Analytics")
    
    if st.session_state.filtered_data is not None:
        data = st.session_state.filtered_data
        
        st.subheader("Create Data Report")
        
        # Add option to save dataset to database
        save_to_db = st.checkbox("Save dataset to database for future use")
        if save_to_db:
            dataset_name = st.text_input("Dataset Name", "My Dataset")
            dataset_description = st.text_area("Dataset Description", "Data imported from file")
            
            if st.button("Save to Database"):
                try:
                    file_type = "csv"  # Default
                    if 'current_file' in st.session_state and st.session_state.current_file:
                        file_type = st.session_state.current_file.split('.')[-1]
                    
                    dataset_id = db.save_dataset(
                        dataset_name,
                        dataset_description,
                        data,
                        file_type
                    )
                    st.success(f"Dataset saved to database with ID: {dataset_id}")
                    
                    # Option to save processing steps
                    if 'processing_steps' in st.session_state and st.session_state.processing_steps:
                        db.save_processed_data(
                            dataset_id,
                            data,
                            st.session_state.processing_steps
                        )
                        st.info("Processing steps also saved")
                        
                except Exception as e:
                    st.error(f"Error saving to database: {e}")
        
        # Report configuration
        report_title = st.text_input("Report Title", "Data Analysis Report")
        include_options = st.multiselect(
            "Include in report",
            ["Data Summary", "Visualizations", "Statistical Analysis", "Data Table"],
            default=["Data Summary", "Visualizations", "Statistical Analysis"]
        )
        
        if st.button("Generate Report"):
            # Create report content
            report = f"# {report_title}\n\n"
            report += f"*Generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
            
            if "Data Summary" in include_options:
                report += "## Data Summary\n\n"
                report += f"- **Dataset size**: {len(data)} rows, {len(data.columns)} columns\n"
                report += f"- **Columns**: {', '.join(data.columns.tolist())}\n\n"
                
                # Add missing values summary
                missing_by_col = data.isna().sum()
                if missing_by_col.sum() > 0:
                    report += "### Missing Values\n\n"
                    for col, count in missing_by_col[missing_by_col > 0].items():
                        report += f"- **{col}**: {count} missing values ({(count/len(data))*100:.2f}%)\n"
                    report += "\n"
            
            if "Statistical Analysis" in include_options:
                report += "## Statistical Analysis\n\n"
                
                # Numerical statistics
                num_cols = data.select_dtypes(include=np.number).columns
                if not num_cols.empty:
                    report += "### Numerical Columns Statistics\n\n"
                    stats_df = data[num_cols].describe().transpose()
                    stats_table = stats_df.to_markdown()
                    report += f"{stats_table}\n\n"
                
                # Categorical statistics
                cat_cols = data.select_dtypes(include=['object']).columns
                if not cat_cols.empty:
                    report += "### Categorical Columns Statistics\n\n"
                    for col in cat_cols:
                        report += f"#### {col}\n\n"
                        value_counts = data[col].value_counts().head(10)
                        vc_table = value_counts.to_markdown()
                        report += f"{vc_table}\n\n"
            
            if "Visualizations" in include_options and st.session_state.generated_charts:
                report += "## Visualizations\n\n"
                report += "*Visualizations are available in the HTML version of this report*\n\n"
                
                for chart in st.session_state.generated_charts:
                    report += f"### {chart['title']}\n\n"
                    report += f"- Type: {chart['type']}\n"
                    if isinstance(chart['x_axis'], str):
                        report += f"- X-axis: {chart['x_axis']}\n"
                    if chart['y_axis'] and isinstance(chart['y_axis'], str):
                        report += f"- Y-axis: {chart['y_axis']}\n"
                    report += "\n"
            
            if "Data Table" in include_options:
                report += "## Data Table\n\n"
                report += "*First 10 rows of the dataset*\n\n"
                table = data.head(10).to_markdown()
                report += f"{table}\n\n"
            
            # Display report preview
            st.markdown("### Report Preview")
            st.markdown(report)
            
            # Export options
            st.download_button(
                "Download report as Markdown",
                report,
                file_name=f"{report_title.replace(' ', '_')}.md",
                mime="text/markdown"
            )
            
            # CSV export option
            csv = data.to_csv(index=False)
            st.download_button(
                "Export data as CSV",
                csv,
                file_name="exported_data.csv",
                mime="text/csv"
            )
    else:
        st.info("Please upload data in the sidebar to create reports.")

with tab4:
    st.header("API Integration")
    
    st.markdown("""
    Technical teams can integrate with this tool through the API endpoints.
    The API server runs on port 8000.
    
    ### API Endpoints
    
    | Endpoint | Method | Description |
    | --- | --- | --- |
    | `/api/docs` | GET | Interactive API documentation |
    | `/api/upload` | POST | Upload data file |
    | `/api/data` | GET | Get the current dataset |
    | `/api/data/summary` | GET | Get dataset summary statistics |
    | `/api/visualize` | POST | Generate a visualization |
    """)
    
    st.subheader("API Example")
    
    code_example = '''
    # Python example using requests
    import requests
    import json
    
    # Upload a CSV file
    with open('data.csv', 'rb') as f:
        response = requests.post('http://localhost:8000/api/upload', files={'file': f})
    
    # Get data summary
    summary = requests.get('http://localhost:8000/api/data/summary')
    
    # Generate a visualization
    viz_config = {
        "chart_type": "Bar Chart",
        "x_axis": "category",
        "y_axis": "value",
        "title": "API Generated Chart"
    }
    
    response = requests.post(
        'http://localhost:8000/api/visualize',
        json=viz_config
    )
    
    # Save the visualization HTML
    with open('visualization.html', 'w') as f:
        f.write(response.json()['html'])
    '''
    
    st.code(code_example, language='python')
    
    if st.session_state.api_started:
        st.success(f"API server is running on http://localhost:8000")
        st.markdown("[View API Documentation](http://localhost:8000/docs)")
    else:
        st.warning("API server is not running. Please restart the application.")

with tab5:
    # Render the Job Matcher UI from the imported function
    render_job_matcher_ui()

# Footer
st.markdown("---")
st.markdown("🔍 IVCA - Intelligent Visualization and Career Analysis - Empowering professionals with data insights")
