import os
import sys
import json
import pandas as pd
import numpy as np

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils.telemetry_util import format_gains_map

def main():
    # Define the path to the gains map CSV file
    gainsmap = os.path.join(parent_dir, 'data', 'SIS-JIG T-Crushing PWO gain map.csv')

    # Read the CSV file
    gains_df = pd.read_csv(gainsmap)

    # Format the gains map using the telemetry_util function
    formatted_gains_df = format_gains_map(gains_df)

    # Replace NaN values with 0
    formatted_gains_df = formatted_gains_df.fillna(0)

    # Convert the formatted DataFrame to a list of dictionaries
    gains_list = formatted_gains_df.to_dict('records')

    # Write the formatted gains map to a JSON file
    output_file = os.path.join(parent_dir, 'reports', 'gains_map.json')
    with open(output_file, 'w') as f:
        json.dump(gains_list, f, indent=2)

    print(f"Formatted gains map has been written to {output_file}")

if __name__ == "__main__":
    main()
