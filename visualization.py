import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_visualization(data, chart_type, x_axis, y_axis=None, color_by=None, 
                        title=None, orientation="Vertical", color_scheme="Plotly", bins=None):
    """
    Create a visualization based on the specified parameters
    
    Parameters:
    data (pd.DataFrame): Input dataframe
    chart_type (str): Type of chart to create
    x_axis (str or list): Column name for x-axis
    y_axis (str, optional): Column name for y-axis
    color_by (str, optional): Column name for color encoding
    title (str, optional): Chart title
    orientation (str): Chart orientation ('Vertical' or 'Horizontal')
    color_scheme (str): Color scheme for the chart
    bins (int, optional): Number of bins for histogram
    
    Returns:
    plotly.graph_objects.Figure: Plotly figure object
    """
    # Handle empty data case
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        fig.update_layout(title=title or "No Data")
        return fig
    
    # Set color scale based on selected scheme
    if color_scheme == "Plotly":
        color_scale = None  # Use Plotly default
    else:
        color_scale = color_scheme.lower()
    
    # Create chart based on type
    if chart_type == "Bar Chart":
        if orientation == "Vertical":
            fig = px.bar(data, x=x_axis, y=y_axis, color=color_by, 
                        title=title, color_continuous_scale=color_scale)
        else:
            fig = px.bar(data, y=x_axis, x=y_axis, color=color_by, 
                        title=title, orientation='h', color_continuous_scale=color_scale)
            
    elif chart_type == "Line Chart":
        fig = px.line(data, x=x_axis, y=y_axis, color=color_by, 
                    title=title, color_discrete_sequence=px.colors.sequential.Plasma 
                    if color_scale else None)
        
    elif chart_type == "Scatter Plot":
        fig = px.scatter(data, x=x_axis, y=y_axis, color=color_by, 
                        title=title, color_continuous_scale=color_scale)
        
    elif chart_type == "Histogram":
        fig = px.histogram(data, x=x_axis, nbins=bins, title=title, 
                          color_discrete_sequence=[px.colors.sequential.Plasma[3]] 
                          if color_scale else None)
        
    elif chart_type == "Box Plot":
        if orientation == "Vertical":
            fig = px.box(data, x=x_axis, y=y_axis, color=color_by, 
                        title=title, color_discrete_sequence=px.colors.sequential.Plasma 
                        if color_scale else None)
        else:
            fig = px.box(data, y=x_axis, x=y_axis, color=color_by, 
                        title=title, color_discrete_sequence=px.colors.sequential.Plasma 
                        if color_scale else None)
        
    elif chart_type == "Pie Chart":
        fig = px.pie(data, names=x_axis, values=y_axis, title=title, 
                    color_discrete_sequence=px.colors.sequential.Plasma 
                    if color_scale else None)
        
    elif chart_type == "Heatmap":
        if isinstance(x_axis, list):
            # For correlation heatmap
            corr_data = data[x_axis].corr()
            fig = px.imshow(corr_data, title=title or "Correlation Matrix",
                           color_continuous_scale=color_scale or "RdBu_r")
        else:
            # General heatmap (e.g., for pivot tables)
            pivot_data = pd.pivot_table(data, values=y_axis, index=x_axis, 
                                      columns=color_by, aggfunc=np.mean)
            fig = px.imshow(pivot_data, title=title, color_continuous_scale=color_scale)
    
    # Apply common layout settings
    fig.update_layout(
        title={
            'text': title,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title=x_axis if isinstance(x_axis, str) else "Features",
        yaxis_title=y_axis if isinstance(y_axis, str) else "Values",
        template="plotly_white",
        height=600
    )
    
    # Add hover data for better interactivity
    if chart_type in ["Bar Chart", "Line Chart", "Scatter Plot"]:
        fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y}")
    
    return fig

def apply_filters(data, filters):
    """
    Apply filters to the dataframe
    
    Parameters:
    data (pd.DataFrame): Input dataframe
    filters (dict): Dictionary of filters with column names as keys and filter values as values
    
    Returns:
    pd.DataFrame: Filtered dataframe
    """
    filtered_data = data.copy()
    
    for column, filter_value in filters.items():
        if column in filtered_data.columns:
            if isinstance(filter_value, tuple) and len(filter_value) == 2:
                # Range filter for numeric columns
                min_val, max_val = filter_value
                filtered_data = filtered_data[(filtered_data[column] >= min_val) & 
                                             (filtered_data[column] <= max_val)]
            
            elif isinstance(filter_value, list):
                # Multi-select filter for categorical columns
                if filter_value:  # Only filter if something is selected
                    filtered_data = filtered_data[filtered_data[column].isin(filter_value)]
    
    return filtered_data

def create_dashboard(data, charts_config):
    """
    Create a dashboard with multiple charts
    
    Parameters:
    data (pd.DataFrame): Input dataframe
    charts_config (list): List of chart configuration dictionaries
    
    Returns:
    plotly.graph_objects.Figure: Plotly figure object with multiple subplots
    """
    # Calculate grid layout
    n_charts = len(charts_config)
    if n_charts <= 2:
        rows, cols = 1, n_charts
    elif n_charts <= 4:
        rows, cols = 2, 2
    else:
        rows = (n_charts + 2) // 3  # Ceiling division
        cols = 3
    
    # Create subplot layout
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=[c.get('title', f"Chart {i+1}") 
                                                             for i, c in enumerate(charts_config)])
    
    # Add each chart to the dashboard
    for i, chart_config in enumerate(charts_config):
        row = (i // cols) + 1
        col = (i % cols) + 1
        
        # Create individual chart
        chart_fig = create_visualization(
            data,
            chart_config.get('type', 'Bar Chart'),
            chart_config.get('x_axis'),
            chart_config.get('y_axis'),
            chart_config.get('color_by'),
            None,  # No title for subplots
            chart_config.get('orientation', 'Vertical'),
            chart_config.get('color_scheme', 'Plotly'),
            chart_config.get('bins')
        )
        
        # Extract the traces from the individual chart and add to dashboard
        for trace in chart_fig.data:
            fig.add_trace(trace, row=row, col=col)
    
    # Update layout
    fig.update_layout(
        height=300 * rows,
        width=300 * cols,
        title_text="Data Dashboard",
        showlegend=False,
        template="plotly_white"
    )
    
    return fig
