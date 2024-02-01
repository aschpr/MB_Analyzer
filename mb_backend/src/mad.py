import os
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

from src.utils import DATA_LOCATION_PATH


# Function to read and process each DBSCAN output file
def process_dbscan_output_file(file_name: str):

    # Read the DBSCAN output file into a DataFrame
    df = pd.read_csv(f"{DATA_LOCATION_PATH}/{file_name}.xyz")

    # Extract the 'depth' column for MAD
    depth = df['depth']

    # Calculate the median of the 'depth' column
    median = depth.median()

    # Calculate the absolute deviation from the median
    abs_deviation = (depth - median).abs()

    # Calculate the median of the absolute deviations
    mad = abs_deviation.median()

    # Define a function to identify outliers based on MAD
    def is_outlier(row):
        return 1 if abs(row['depth'] - median) > 3 * mad else 0

    # Apply the function to each row in the DataFrame to identify outliers
    df['mad_outlier'] = df.apply(is_outlier, axis=1)

    # Reset the index
    df.reset_index(drop=True, inplace=True)

    # Save the processed file with the addition "mad" to the filename
    # output_file_path = file_path.replace('_std.', '_mad.')
    df.to_csv(f"{DATA_LOCATION_PATH}/{file_name}_mad.xyz")

    return df
