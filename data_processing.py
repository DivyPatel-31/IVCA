import pandas as pd
import numpy as np
from sklearn import preprocessing

def clean_data(data, method="drop_rows"):
    """
    Clean the data by handling missing values
    
    Parameters:
    data (pd.DataFrame): Input dataframe
    method (str): Method to handle missing values:
                 - drop_rows: Drop rows with missing values
                 - fill_with_mean_mode: Fill missing values with mean (numeric) or mode (categorical)
                 - fill_with_zeros: Fill missing values with zeros
                 
    Returns:
    pd.DataFrame: Cleaned dataframe
    """
    df = data.copy()
    
    if method == "drop_rows":
        df = df.dropna()
    
    elif method == "fill_with_mean_mode":
        # Fill numeric columns with mean
        for col in df.select_dtypes(include=np.number).columns:
            df[col] = df[col].fillna(df[col].mean())
        
        # Fill categorical columns with mode
        for col in df.select_dtypes(include=['object']).columns:
            if not df[col].empty and df[col].mode().size > 0:
                df[col] = df[col].fillna(df[col].mode()[0])
    
    elif method == "fill_with_zeros":
        df = df.fillna(0)
    
    return df

def transform_data(data, method="none"):
    """
    Transform the data using various methods
    
    Parameters:
    data (pd.DataFrame): Input dataframe
    method (str): Transformation method:
                 - normalize_numeric_columns: Scale numeric features to 0-1 range
                 - log_transform: Apply log transformation to numeric columns
                 - one_hot_encode_categorical: One-hot encode categorical variables
                 
    Returns:
    pd.DataFrame: Transformed dataframe
    """
    df = data.copy()
    
    if method == "normalize_numeric_columns":
        scaler = preprocessing.MinMaxScaler()
        for col in df.select_dtypes(include=np.number).columns:
            df[col] = scaler.fit_transform(df[[col]])
            
    elif method == "log_transform":
        for col in df.select_dtypes(include=np.number).columns:
            # Add small constant to handle zeros
            if (df[col] <= 0).any():
                df[col] = df[col] - df[col].min() + 1  # ensure all values > 0
            df[col] = np.log(df[col])
            
    elif method == "one_hot_encode_categorical":
        # One-hot encode categorical variables with fewer than 10 unique values
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() < 10:  # Only encode if fewer than 10 categories
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=False)
                df = pd.concat([df, dummies], axis=1)
                df = df.drop(col, axis=1)
    
    return df

def get_data_summary(data):
    """
    Generate summary statistics for the dataset
    
    Parameters:
    data (pd.DataFrame): Input dataframe
    
    Returns:
    dict: Dictionary containing summary statistics
    """
    if data is None or data.empty:
        return {"error": "No data available"}
    
    summary = {
        "shape": {"rows": len(data), "columns": len(data.columns)},
        "columns": list(data.columns),
        "missing_values": int(data.isna().sum().sum()),
        "missing_percentage": float((data.isna().sum().sum() / (data.shape[0] * data.shape[1])) * 100),
        "numeric_columns": {},
        "categorical_columns": {}
    }
    
    # Numeric column statistics
    for col in data.select_dtypes(include=np.number).columns:
        summary["numeric_columns"][col] = {
            "mean": float(data[col].mean()),
            "median": float(data[col].median()),
            "std": float(data[col].std()),
            "min": float(data[col].min()),
            "max": float(data[col].max()),
            "missing": int(data[col].isna().sum())
        }
    
    # Categorical column statistics
    for col in data.select_dtypes(include=['object']).columns:
        value_counts = data[col].value_counts().head(5).to_dict()
        summary["categorical_columns"][col] = {
            "unique_values": int(data[col].nunique()),
            "top_values": value_counts,
            "missing": int(data[col].isna().sum())
        }
    
    return summary

def detect_outliers(data, method="zscore", threshold=3):
    """
    Detect outliers in numeric columns
    
    Parameters:
    data (pd.DataFrame): Input dataframe
    method (str): Outlier detection method ('zscore' or 'iqr')
    threshold (float): Threshold for outlier detection
    
    Returns:
    dict: Dictionary with column names as keys and lists of outlier indices as values
    """
    outliers = {}
    
    for col in data.select_dtypes(include=np.number).columns:
        col_data = data[col].dropna()
        
        if method == "zscore":
            z_scores = np.abs((col_data - col_data.mean()) / col_data.std())
            outlier_indices = z_scores[z_scores > threshold].index.tolist()
        
        elif method == "iqr":
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            outlier_indices = col_data[(col_data < (Q1 - threshold * IQR)) | 
                                       (col_data > (Q3 + threshold * IQR))].index.tolist()
        
        if outlier_indices:
            outliers[col] = outlier_indices
    
    return outliers
