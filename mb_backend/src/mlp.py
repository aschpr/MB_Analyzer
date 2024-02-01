import os

import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
import joblib  # for loading the model

from src.utils import DATA_LOCATION_PATH


# Load your data from a Feather file

def process_ml_output_file(file_name: str):
    data_df = pd.read_csv(f"{DATA_LOCATION_PATH}/{file_name}.xyz")

    # Specify the columns to be used as features
    X = data_df[['lat', 'lon', 'depth', 'std_dev_depth_100m', 'mean_depth_100m', 'normalized_distance_100m']]

    # Check for NaN values in each column
    nan_columns = X.columns[X.isna().any()]
    num_nan_columns = len(nan_columns)

    # Print the number of columns with NaN values
    print("Number of columns with NaN values: {}".format(num_nan_columns))

    # Replace NaN values with 0
    X.fillna(0, inplace=True)

    # Scale the data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Load the trained model from file
    model_file_path = os.getcwd() + "/src" + "/mlp_model.pkl"
    clf = joblib.load(model_file_path)

    # Predict labels for your data
    y_pred = clf.predict(X_scaled)

    # Add predicted labels to your data DataFrame
    data_df['mlp_outlier'] = y_pred

    data_df.to_csv(f"{DATA_LOCATION_PATH}/{file_name}_ml.xyz")
