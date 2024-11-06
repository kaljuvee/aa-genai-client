import pandas as pd
import logging
from typing import Optional, Dict, Any, Union, Callable

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Single comprehensive mapping dictionary
GAINS_COLUMN_MAPPING: Dict[str, Union[str, Dict[str, str], Callable]] = {
    # Basic column renames
    'CVNAME': 'Variable Type',
    'CVAPETTAG': 'Variable Name',
    
    # Type mapping
    'TYPE': {
        'MV': 'Manipulated Variable',
        'CV': 'Controlled Variable',
        'DV': 'Disturbance Variable'
    },
    
    # MVDVNAME formatting
    'MVDVNAME': lambda x: x.replace('_', ' ').replace('Tert Crusher', 'Tertiary Crusher'),
    
    # Columns to keep as-is
    'MVDVAPETTAG': 'MVDVAPETTAG',
    'MVDVNUMBER': 'MVDVNUMBER',
    'GAIN-VALUE': 'GAIN-VALUE'
}

def load_and_filter_data(datasource: str, apc_name: str) -> pd.DataFrame:
    """
    Load data from a CSV file and filter it based on the APC name.

    Args:
        datasource (str): Path to the CSV data file.
        apc_name (str): APC name to filter the data.

    Returns:
        pd.DataFrame: Filtered DataFrame containing only rows with the specified APC name.
    """
    try:
        logging.info(f"Loading data from {datasource}")
        df = pd.read_csv(datasource)
        
        logging.info(f"Filtering data for APC: {apc_name}")
        filtered_df = df[df['IDX_TagName'].str.contains(apc_name, case=True, na=False)]
        
        logging.info(f"Filtered data shape: {filtered_df.shape}")
        return filtered_df
    
    except FileNotFoundError:
        logging.error(f"File not found: {datasource}")
        raise
    except pd.errors.EmptyDataError:
        logging.error(f"The file {datasource} is empty")
        raise
    except Exception as e:
        logging.error(f"An error occurred while processing the data: {str(e)}")
        raise

def get_treshold_violations(df):
    # Create masks for violations
    below_min_mask = df['ValueReal'] < df['IDX_Minimum']
    above_max_mask = df['ValueReal'] > df['IDX_Maximum']
    
    # Combine masks to get all violations
    violations_df = df[below_min_mask | above_max_mask].copy()
    
    # Add a new 'message' column
    violations_df['message'] = violations_df.apply(
        lambda row: f"{row['IDX_TagName']}: Current value {row['ValueReal']} is {'less than Minimum' if row['ValueReal'] < row['IDX_Minimum'] else 'greater than Maximum'} value {row['IDX_Minimum'] if row['ValueReal'] < row['IDX_Minimum'] else row['IDX_Maximum']}",
        axis=1
    )
    
    return violations_df

def format_gains_map(df: pd.DataFrame, log_level: str = 'INFO') -> Optional[pd.DataFrame]:
    try:
        # Validate input
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
            
        # Check for missing columns
        missing_columns = [col for col in GAINS_COLUMN_MAPPING.keys() if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
            
        # Create a copy of the DataFrame to avoid modifying the original
        df_transformed = df.copy()
        logging.info("Created copy of input DataFrame")
        
        # Add new filtering conditions
        logging.info("Applying filters for J140-BIN and PROFIT_AVERAGE_STOCKPILE_LEVEL")
        df_transformed = df_transformed[
            df_transformed['CVAPETTAG'].str.contains('J140-BIN', case=True, na=False) &
            df_transformed['GAIN-TAG'].str.contains('PROFIT_AVERAGE_BIN_LEVEL', case=True, na=False)
        ]
        logging.info(f"After filtering, DataFrame shape: {df_transformed.shape}")
        
        # Process each column according to its mapping type
        for col, mapping in GAINS_COLUMN_MAPPING.items():
            try:
                if isinstance(mapping, str):
                    # Simple column rename
                    if col in df_transformed.columns:
                        df_transformed = df_transformed.rename(columns={col: mapping})
                        logging.debug(f"Renamed column {col} to {mapping}")
                
                elif isinstance(mapping, dict):
                    # Dictionary mapping (e.g., for TYPE column)
                    if col in df_transformed.columns:
                        df_transformed[col] = df_transformed[col].map(mapping)
                        unmapped = df_transformed[col].isna()
                        if unmapped.any():
                            logging.warning(f"Found unmapped values in {col}: {df_transformed.loc[unmapped, col].unique()}")
                            df_transformed[col] = df_transformed[col].fillna(df_transformed[col])
                        logging.debug(f"Applied dictionary mapping to column {col}")
                
                elif callable(mapping):
                    # Function mapping (e.g., for MVDVNAME)
                    if col in df_transformed.columns:
                        df_transformed[col] = df_transformed[col].apply(mapping)
                        logging.debug(f"Applied function mapping to column {col}")
                
                else:
                    logging.warning(f"Unrecognized mapping type for column {col}: {type(mapping)}")
            
            except Exception as e:
                logging.error(f"Error processing column {col}: {e}")
                raise
        
        # Validate transformations
        null_counts = df_transformed.isnull().sum()
        if null_counts.any():
            logging.warning(f"Found null values after transformation:\n{null_counts[null_counts > 0]}")
        
        logging.info("Successfully completed all transformations")
        return df_transformed
        
    except Exception as e:
        logging.error(f"An error occurred during transformation: {e}")
        raise
        
    finally:
        logging.debug("Format gains map function execution completed")
