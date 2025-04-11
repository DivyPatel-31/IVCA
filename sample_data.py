import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sales_data():
    """Generate a sample sales dataset"""
    np.random.seed(42)
    
    # Create date range for the past year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Product categories
    categories = ['Electronics', 'Clothing', 'Home & Kitchen', 'Books', 'Sports']
    
    # Regions
    regions = ['North', 'South', 'East', 'West', 'Central']
    
    # Generate random data
    n_records = len(date_range) * 5  # 5 records per day
    
    data = {
        'Date': np.random.choice(date_range, n_records),
        'Category': np.random.choice(categories, n_records),
        'Region': np.random.choice(regions, n_records),
        'Sales': np.random.normal(1000, 500, n_records).round(2),
        'Units': np.random.randint(1, 100, n_records),
        'Discount': np.random.choice([0, 0.05, 0.1, 0.2, 0.3], n_records),
        'CustomerSatisfaction': np.random.randint(1, 6, n_records)
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add some calculated columns
    df['Revenue'] = df['Sales'] * df['Units']
    df['DiscountAmount'] = df['Revenue'] * df['Discount']
    df['NetRevenue'] = df['Revenue'] - df['DiscountAmount']
    
    # Sort by date
    df = df.sort_values('Date')
    
    return df

def generate_customer_data():
    """Generate a sample customer dataset"""
    np.random.seed(43)
    
    n_customers = 1000
    
    # Age groups
    age_groups = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
    
    # Genders
    genders = ['Male', 'Female', 'Non-binary', 'Prefer not to say']
    
    # Cities
    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 
              'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose']
    
    # Generate customer data
    data = {
        'CustomerID': range(1001, 1001 + n_customers),
        'Age': np.random.randint(18, 85, n_customers),
        'AgeGroup': np.random.choice(age_groups, n_customers),
        'Gender': np.random.choice(genders, n_customers),
        'City': np.random.choice(cities, n_customers),
        'SignupDate': pd.date_range(
            start=datetime.now() - timedelta(days=1000),
            periods=n_customers
        ),
        'TotalPurchases': np.random.randint(0, 50, n_customers),
        'TotalSpent': np.random.gamma(shape=5, scale=100, size=n_customers).round(2),
        'HasSubscription': np.random.choice([True, False], n_customers, p=[0.3, 0.7]),
        'LastPurchaseDate': pd.date_range(
            start=datetime.now() - timedelta(days=365),
            periods=n_customers
        )
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add some calculated fields
    df['DaysSinceLastPurchase'] = (datetime.now() - df['LastPurchaseDate']).dt.days
    df['AvgPurchaseValue'] = df['TotalSpent'] / df['TotalPurchases'].replace(0, 1)
    df['CustomerLifetimeDays'] = (datetime.now() - df['SignupDate']).dt.days
    
    return df

def generate_hr_data():
    """Generate a sample HR dataset"""
    np.random.seed(44)
    
    n_employees = 500
    
    # Departments
    departments = ['Sales', 'Marketing', 'IT', 'HR', 'Finance', 'Operations', 'R&D']
    
    # Job levels
    job_levels = ['Entry', 'Associate', 'Senior', 'Manager', 'Director', 'Executive']
    
    # Performance ratings
    ratings = ['Poor', 'Below Average', 'Average', 'Good', 'Excellent']
    
    # Start dates within the last 10 years
    start_dates = pd.date_range(
        start=datetime.now() - timedelta(days=3650),
        periods=n_employees
    )
    
    # Generate employee data
    data = {
        'EmployeeID': range(1, n_employees + 1),
        'Department': np.random.choice(departments, n_employees),
        'JobLevel': np.random.choice(job_levels, n_employees),
        'Salary': np.random.gamma(shape=10, scale=5000, size=n_employees).round(-2),
        'YearsExperience': np.random.randint(0, 30, n_employees),
        'StartDate': start_dates,
        'PerformanceRating': np.random.choice(ratings, n_employees, 
                                            p=[0.05, 0.15, 0.4, 0.3, 0.1]),
        'Absences': np.random.poisson(lam=5, size=n_employees),
        'PromotionEligible': np.random.choice([True, False], n_employees),
        'TrainingHours': np.random.poisson(lam=20, size=n_employees),
        'RemoteWorkDays': np.random.randint(0, 6, n_employees)
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add some calculated fields
    df['YearsAtCompany'] = ((datetime.now() - df['StartDate']).dt.days / 365).round(1)
    df['SalaryPerYearExperience'] = (df['Salary'] / df['YearsExperience'].replace(0, 1)).round(0)
    df['SalaryCategory'] = pd.cut(df['Salary'], 
                                bins=[0, 30000, 60000, 90000, 150000, float('inf')],
                                labels=['Low', 'Below Average', 'Average', 'Above Average', 'High'])
    
    return df

def get_sample_datasets():
    """Return a dictionary of sample datasets"""
    datasets = {
        'Sales Data': generate_sales_data(),
        'Customer Analytics': generate_customer_data(),
        'HR Data': generate_hr_data()
    }
    return datasets

if __name__ == "__main__":
    # Test generating the datasets
    for name, dataset in get_sample_datasets().items():
        print(f"{name}: {dataset.shape}, Memory usage: {dataset.memory_usage().sum() / 1024 / 1024:.2f} MB")
        print(dataset.head(2))
        print("\n" + "-"*80 + "\n")