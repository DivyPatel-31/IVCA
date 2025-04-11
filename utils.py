import pandas as pd
import numpy as np
import io
import base64
import json
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def get_file_extension(filename):
    """
    Get the file extension from a filename
    
    Parameters:
    filename (str): Name of the file
    
    Returns:
    str: File extension (without the dot)
    """
    return filename.split(".")[-1].lower()

def infer_data_types(data):
    """
    Infer data types for each column in the dataframe
    
    Parameters:
    data (pd.DataFrame): Input dataframe
    
    Returns:
    dict: Dictionary with column names as keys and inferred data types as values
    """
    data_types = {}
    
    for column in data.columns:
        if pd.api.types.is_numeric_dtype(data[column]):
            if data[column].dropna().apply(lambda x: x.is_integer() if isinstance(x, float) else True).all():
                data_types[column] = "integer"
            else:
                data_types[column] = "float"
        elif pd.api.types.is_datetime64_dtype(data[column]):
            data_types[column] = "datetime"
        elif data[column].nunique() < 10 and data[column].nunique() / len(data[column]) < 0.1:
            data_types[column] = "categorical"
        else:
            data_types[column] = "text"
    
    return data_types

def get_fig_as_base64(fig):
    """
    Convert a plotly figure to a base64 string
    
    Parameters:
    fig (plotly.graph_objects.Figure): Plotly figure
    
    Returns:
    str: Base64 encoded string of the figure
    """
    img_bytes = fig.to_image(format="png")
    encoded = base64.b64encode(img_bytes).decode("ascii")
    return f"data:image/png;base64,{encoded}"

def run_quick_linear_regression(data, x_columns, y_column):
    """
    Run a quick linear regression on the data
    
    Parameters:
    data (pd.DataFrame): Input dataframe
    x_columns (list): List of column names for independent variables
    y_column (str): Column name for dependent variable
    
    Returns:
    dict: Dictionary containing regression results
    """
    # Prepare data
    X = data[x_columns].dropna()
    y = data[y_column].loc[X.index]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    # Get coefficients
    coefficients = {}
    for i, col in enumerate(x_columns):
        coefficients[col] = float(model.coef_[i])
    
    return {
        "coefficients": coefficients,
        "intercept": float(model.intercept_),
        "mse": float(mse),
        "r2": float(r2),
        "test_size": len(X_test)
    }

def run_kmeans_clustering(data, columns, n_clusters=3):
    """
    Run K-means clustering on the data
    
    Parameters:
    data (pd.DataFrame): Input dataframe
    columns (list): List of column names to use for clustering
    n_clusters (int): Number of clusters
    
    Returns:
    dict: Dictionary containing clustering results
    """
    # Prepare data
    X = data[columns].dropna()
    
    # Scale the data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Run K-means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)
    
    # Add cluster labels to the original data
    result_data = X.copy()
    result_data['cluster'] = clusters
    
    # Calculate cluster statistics
    cluster_stats = {}
    for i in range(n_clusters):
        cluster_data = result_data[result_data['cluster'] == i]
        stats = {}
        for col in columns:
            stats[col] = {
                "mean": float(cluster_data[col].mean()),
                "std": float(cluster_data[col].std()),
                "min": float(cluster_data[col].min()),
                "max": float(cluster_data[col].max())
            }
        cluster_stats[f"cluster_{i}"] = stats
    
    return {
        "cluster_stats": cluster_stats,
        "cluster_sizes": result_data['cluster'].value_counts().to_dict(),
        "cluster_centers": kmeans.cluster_centers_.tolist(),
        "inertia": float(kmeans.inertia_)
    }

def generate_correlation_matrix(data):
    """
    Generate a correlation matrix for numeric columns
    
    Parameters:
    data (pd.DataFrame): Input dataframe
    
    Returns:
    dict: Dictionary containing correlation matrix
    """
    numeric_data = data.select_dtypes(include=np.number)
    
    if numeric_data.empty:
        return {"error": "No numeric columns found"}
    
    corr_matrix = numeric_data.corr().round(2)
    
    # Convert to a format suitable for JSON
    corr_dict = {}
    for col in corr_matrix.columns:
        corr_dict[col] = corr_matrix[col].to_dict()
    
    # Find top correlations
    corr_pairs = []
    for i, col1 in enumerate(corr_matrix.columns):
        for j, col2 in enumerate(corr_matrix.columns):
            if i < j:  # To avoid duplicates and self-correlations
                corr_pairs.append({
                    "columns": [col1, col2],
                    "correlation": float(corr_matrix.loc[col1, col2])
                })
    
    # Sort by absolute correlation value
    corr_pairs = sorted(corr_pairs, key=lambda x: abs(x["correlation"]), reverse=True)
    
    return {
        "correlation_matrix": corr_dict,
        "top_correlations": corr_pairs[:10]  # Top 10 correlations
    }
