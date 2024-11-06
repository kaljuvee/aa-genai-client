import pandas as pd
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, inspect
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv
from pathlib import Path
import numpy as np
import logging
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URI from environment variables
DATABASE_URL = os.getenv('DATABASE_URL')
logger.info(f"Connecting to database: {DATABASE_URL}")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create declarative base using updated import
Base = declarative_base()

def infer_sql_type(series):
    """Infer SQLAlchemy column type from pandas series"""
    dtype = series.dtype
    sample_value = series.iloc[0] if not series.empty else None
    
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return DateTime
    elif pd.api.types.is_float_dtype(dtype):
        return Float
    elif pd.api.types.is_integer_dtype(dtype):
        return Integer
    elif pd.api.types.is_bool_dtype(dtype):
        return Boolean
    elif isinstance(sample_value, str) or pd.api.types.is_string_dtype(dtype):
        return String
    else:
        return String  # Default to String for unknown types

def create_table_class(df, table_name):
    """Dynamically create SQLAlchemy model class from DataFrame"""
    class_attrs = {
        '__tablename__': table_name,
        '__table_args__': {'extend_existing': True},
        # Add id column as primary key
        'id': Column(Integer, primary_key=True, autoincrement=True)
    }
    
    # Add columns
    for column in df.columns:
        sql_type = infer_sql_type(df[column])
        if sql_type == String:
            class_attrs[column] = Column(String(1000), nullable=True)
        else:
            class_attrs[column] = Column(sql_type, nullable=True)
    
    # Create and return the class
    return type(table_name, (Base,), class_attrs)

def verify_table_exists(engine, table_name):
    """Verify if table exists and has data"""
    inspector = inspect(engine)
    if table_name in inspector.get_table_names():
        # Check if table has any rows using the new SQLAlchemy 2.0 syntax
        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            logger.info(f"Table '{table_name}' exists with {result} rows")
            return True
    logger.warning(f"Table '{table_name}' does not exist")
    return False

def main():
    # Get all ADX CSV files from data directory
    data_dir = Path('data')
    adx_files = list(data_dir.glob('adx*.csv'))
    
    if not adx_files:
        logger.error(f"No ADX CSV files found in {data_dir}")
        return
    
    logger.info(f"Found {len(adx_files)} ADX CSV files to process")
    
    # Create tables for each CSV file
    for file_path in adx_files:
        logger.info(f"Processing file: {file_path}")
        
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            logger.info(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
            
            # Clean column names (remove special characters, spaces)
            df.columns = [col.replace(' ', '_').replace('-', '_') for col in df.columns]
            
            # Create table name from file name
            table_name = file_path.stem.lower()
            
            # Create model class
            table_class = create_table_class(df, table_name)
            
            # Create table in database
            table_class.__table__.create(engine, checkfirst=True)
            logger.info(f"Created table schema: {table_name}")
            
            # Create session
            Session = sessionmaker(bind=engine)
            session = Session()
            
            try:
                # Convert DataFrame to dict and insert data
                data = df.to_dict('records')
                
                # Insert in batches to handle large datasets
                batch_size = 1000
                total_batches = (len(data) + batch_size - 1) // batch_size
                
                for i in range(0, len(data), batch_size):
                    batch = data[i:i + batch_size]
                    current_batch = (i // batch_size) + 1
                    logger.info(f"Inserting batch {current_batch}/{total_batches} for {table_name}")
                    session.bulk_insert_mappings(table_class, batch)
                
                session.commit()
                
                # Verify table creation and data insertion
                if verify_table_exists(engine, table_name):
                    logger.info(f"Successfully created and populated table: {table_name}")
                else:
                    logger.error(f"Table verification failed for: {table_name}")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error processing {table_name}: {str(e)}", exc_info=True)
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
