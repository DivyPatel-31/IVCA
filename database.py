import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, JSON, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# Get database URL from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')

# Create database engine
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define database models
class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    file_type = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    column_names = Column(JSON)  # Store column names as JSON
    row_count = Column(Integer)
    
class Visualization(Base):
    __tablename__ = "visualizations"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    chart_type = Column(String)
    config = Column(JSON)  # Store chart configuration as JSON
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
class SavedData(Base):
    __tablename__ = "saved_data"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, index=True)
    data_table = Column(String)  # Name of dynamically created table
    is_processed = Column(Integer, default=0)  # 0: original, 1: processed
    processing_steps = Column(JSON, nullable=True)  # Store processing steps as JSON
    created_at = Column(DateTime, default=datetime.now)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Database operations
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def save_dataset(name, description, df, file_type):
    """Save dataset metadata and create data table"""
    db = get_db()
    try:
        # Create dataset record
        dataset = Dataset(
            name=name,
            description=description,
            file_type=file_type,
            column_names=json.dumps(df.columns.tolist()),
            row_count=len(df)
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        # Create table name
        table_name = f"dataset_{dataset.id}_data"
        
        # Save data to new table
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        
        # Create saved_data record
        saved_data = SavedData(
            dataset_id=dataset.id,
            data_table=table_name,
            is_processed=0
        )
        db.add(saved_data)
        db.commit()
        
        return dataset.id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
        
def save_visualization(dataset_id, name, description, chart_type, config):
    """Save visualization metadata"""
    db = get_db()
    try:
        viz = Visualization(
            dataset_id=dataset_id,
            name=name,
            description=description,
            chart_type=chart_type,
            config=json.dumps(config)
        )
        db.add(viz)
        db.commit()
        db.refresh(viz)
        return viz.id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
        
def save_processed_data(dataset_id, df, processing_steps):
    """Save processed data"""
    db = get_db()
    try:
        # Create table name
        table_name = f"dataset_{dataset_id}_processed_data"
        
        # Save data to new table
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        
        # Create saved_data record
        saved_data = SavedData(
            dataset_id=dataset_id,
            data_table=table_name,
            is_processed=1,
            processing_steps=json.dumps(processing_steps)
        )
        db.add(saved_data)
        db.commit()
        
        return saved_data.id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
        
def get_dataset(dataset_id):
    """Get dataset metadata"""
    db = get_db()
    try:
        return db.query(Dataset).filter(Dataset.id == dataset_id).first()
    finally:
        db.close()
        
def get_dataset_data(dataset_id, processed=False):
    """Get dataset data"""
    db = get_db()
    try:
        # Find the appropriate saved_data record
        saved_data = db.query(SavedData).filter(
            SavedData.dataset_id == dataset_id,
            SavedData.is_processed == (1 if processed else 0)
        ).order_by(SavedData.created_at.desc()).first()
        
        if not saved_data:
            return None
            
        # Load data from table
        return pd.read_sql_table(saved_data.data_table, engine)
    finally:
        db.close()
        
def get_all_datasets():
    """Get all datasets"""
    db = get_db()
    try:
        return db.query(Dataset).order_by(Dataset.created_at.desc()).all()
    finally:
        db.close()
        
def get_dataset_visualizations(dataset_id):
    """Get all visualizations for a dataset"""
    db = get_db()
    try:
        return db.query(Visualization).filter(
            Visualization.dataset_id == dataset_id
        ).order_by(Visualization.created_at.desc()).all()
    finally:
        db.close()
        
def get_visualization(viz_id):
    """Get visualization by ID"""
    db = get_db()
    try:
        return db.query(Visualization).filter(Visualization.id == viz_id).first()
    finally:
        db.close()
        
def get_all_visualizations():
    """Get all visualizations"""
    db = get_db()
    try:
        return db.query(Visualization).order_by(Visualization.created_at.desc()).all()
    finally:
        db.close()
        
def delete_dataset(dataset_id):
    """Delete dataset and all associated data"""
    db = get_db()
    try:
        # Get all saved data records
        saved_data_records = db.query(SavedData).filter(SavedData.dataset_id == dataset_id).all()
        
        # Drop data tables
        metadata = MetaData()
        for record in saved_data_records:
            table = Table(record.data_table, metadata)
            table.drop(engine, checkfirst=True)
            db.delete(record)
        
        # Delete visualizations
        visualizations = db.query(Visualization).filter(Visualization.dataset_id == dataset_id).all()
        for viz in visualizations:
            db.delete(viz)
            
        # Delete dataset record
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if dataset:
            db.delete(dataset)
            
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
        
def delete_visualization(viz_id):
    """Delete visualization"""
    db = get_db()
    try:
        viz = db.query(Visualization).filter(Visualization.id == viz_id).first()
        if viz:
            db.delete(viz)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# Initialize database
create_tables()