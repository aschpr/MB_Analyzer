import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import re
from requests import Response

from src.database import MBSQLDatabase
from src.kmeans import process_kmeans_output_file
from src.mad import process_dbscan_output_file
from src.mlp import process_ml_output_file
from src.utils import ProcessingSettings, FILE_SERVER_URL, process_file, ScriptSetting, DATA_LOCATION_PATH, \
    FILE_SQL_NAME
from os import listdir
from os.path import isfile, join
from fastapi.middleware.gzip import GZipMiddleware

import requests

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware)


@app.get("/get-lod-file-names")
def get_current_file_names():
    """
    Get all file names from the file server.
    :return:
    """
    res: Response = requests.get(FILE_SERVER_URL)

    file_names = re.findall(r'href="([^"]+)"', res.content.decode("utf-8"))
    file_names_filtered_for_lod = [f for f in file_names if "lod" in f]
    # filter for unique file names
    file_names = set([f.split("_lod_")[0] for f in file_names_filtered_for_lod])
    return list(file_names)


@app.get("/get-raw-file-names")
def get_raw_file_names():
    """
    Get all file names from the file server.
    :return:
    """
    res: Response = requests.get(FILE_SERVER_URL)

    file_names = re.findall(r'href="([^"]+)"', res.content.decode("utf-8"))
    file_names_filtered_for_raw = [f for f in file_names if f.endswith(".xyz")]
    return list(file_names_filtered_for_raw)


@app.post("/post-process-file/")
async def post_process_file_for_lod(settings: ProcessingSettings):
    """
    Process the file with the given settings.
    :param settings:
    :return:
    """
    process_file(settings.filename, settings.sep, settings.to_utm)
    return True


@app.post("/post-execute-script/")
async def post_execute_script(scripts: ScriptSetting):
    """
    Execute the script with the given settings.
    :param scripts:
    :return:
    """
    if scripts.stat_based:
        process_dbscan_output_file(scripts.filename)
    if scripts.k_means:
        process_kmeans_output_file(scripts.filename)
    if scripts.ml:
        process_ml_output_file(scripts.filename)
    return True

@app.post("/post-file-delete/")
def post_file_delete(file_name: dict):
    """
    Delete the file with the given name.
    :param file_name:
    :return:
    """
    file_name = file_name["file_name"]

    onlyfiles = [f for f in listdir(DATA_LOCATION_PATH) if isfile(join(DATA_LOCATION_PATH, f))]

    filtered_files = [f for f in onlyfiles if file_name.split(".")[0] in f]

    try:
        for f in filtered_files:
            os.remove(f"{DATA_LOCATION_PATH}/{f}")
        return True
    except OSError:
        return False

@app.post("/post-execute-script/")
async def save_settings_to_db():
    """
    Save the settings to the database.
    :return:
    """
    db = MBSQLDatabase(f"{DATA_LOCATION_PATH}{FILE_SQL_NAME}")
    table_name: str = "settings"
    db.create_new_table(table_name)
    db.insert_data(table_name, [])
    data = db.select_data(table_name)
    del db

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)
