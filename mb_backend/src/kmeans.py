import os
import pandas as pd
from sklearn.cluster import KMeans
from concurrent.futures import ProcessPoolExecutor

from src.utils import DATA_LOCATION_PATH


# Function to read and process each k-means clustering output file
def process_kmeans_output_file(file_name: str):
    # Read the k-means clustering output file into a DataFrame
    df = pd.read_csv(f"{DATA_LOCATION_PATH}/{file_name}.xyz")

    # Extract the columns used for k-means clustering
    X = df[['lat', 'lon', 'depth']]

    # Perform k-means clustering
    kmeans = KMeans(n_clusters=4, random_state=0)
    df['kmeans_cluster'] = kmeans.fit_predict(X)

    # Calculate the distance from each data point to the center of its assigned cluster
    df['kmeans_distance'] = kmeans.transform(X).min(axis=1)

    # Mark soundings with a large distance as outliers
    df['kmeans_outlier'] = 0
    df.loc[df['kmeans_distance'] > df['kmeans_distance'].median(), 'kmeans_outlier'] = 1

    # Reset the index
    df.reset_index(drop=True, inplace=True)

    # Save the processed file with the addition "kmeans" to the filename
    #output_file_path = file_path.replace('_lof.', '_kmeans.')
    df.to_csv(f"{DATA_LOCATION_PATH}/{file_name}_kmeans.xyz")

    return df
