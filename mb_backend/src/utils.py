import dataclasses
import math
import os
from itertools import groupby
from operator import attrgetter
from typing import List, Dict, Tuple, Optional
import numpy as np
import pypcd

from src.multibeam_loader import MBEntry, MBLoader

DATA_LOCATION_PATH = os.path.abspath(os.path.join(os.path.dirname( __name__ ), '..', 'data'))
FILE_SERVER_URL = "http://127.0.0.1:3333/"

FILE_DATA_NAME = "mb_raw.xyz"
FILE_SQL_NAME = "mb_viewer.db"

def calculate_distance(entry1: MBEntry, entry2: MBEntry) -> float:
    """
    Calculate Euclidean distance between two MBEntry points in 2D space.
    Ignore h_depth for grouping.
    """
    return math.sqrt((entry1.easting - entry2.easting) ** 2 +
                     (entry1.northing - entry2.northing) ** 2)


def group_points_into_chunks(mb_data: List[MBEntry], n: int) -> List[MBEntry]:
    """
    Group points in mb_data into n chunks based on their proximity in 2D space.
    Set chunk_index for each point.
    """
    sorted_mb_data = sorted(mb_data, key=lambda x: (x.easting, x.northing))
    chunk_size = len(sorted_mb_data) // n

    chunks = []
    for i in range(n):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size if i < n - 1 else None
        current_chunk = sorted_mb_data[start_idx:end_idx]

        # Set chunk_index for points in the current chunk
        for mb_entry in current_chunk:
            mb_entry.chunk_index = f"Chunk_{i + 1}"

        chunks.extend(current_chunk)

    return chunks


def group_by_chunk_index(entries: List[MBEntry]) -> Dict[str, List[MBEntry]]:
    index_dict = {}
    for d in entries:
        index_dict.setdefault(d.chunk_index, []).append(d)
    return index_dict


def find_coordinate_boundaries(entries: List[MBEntry]) -> Optional[Tuple[float, float, float, float]]:
    if not entries:
        return None  # Return None if the list is empty

    eastings = np.array([entry.easting for entry in entries])
    northings = np.array([entry.northing for entry in entries])

    min_easting, max_easting = np.min(eastings), np.max(eastings)
    min_northing, max_northing = np.min(northings), np.max(northings)

    return min_easting, max_easting, min_northing, max_northing


@dataclasses.dataclass
class ProcessingSettings:
    filename: str
    sep: str
    to_utm: bool


def process_file(filename: str, sep: str, to_utm: bool):

    mb_data = []
    mb_loader: MBLoader = MBLoader(f"{DATA_LOCATION_PATH}/{filename}", to_utm=to_utm, separator=sep)

    # Load data into memory
    for entry in mb_loader.load_data_generator(10_000_000):
        mb_data.append({
            "x": entry.easting,
            "y": entry.h_depth,
            "z": entry.northing
        })

    # Convert the list of dictionaries to a NumPy array
    dtype_new = np.dtype({'names': ["x", "y", "z"], 'formats': ['<f8', '<f8', '<f8']})
    mb_data_array = np.array([(d['x'], d['y'], d['z']) for d in mb_data], dtype=dtype_new)

    for p in [0.1, 0.2, 0.5, 1]:
        num_elements = int(p * len(mb_data_array))
        selected_data = np.random.choice(mb_data_array, size=num_elements, replace=False)
        save_name = f"{filename}_lod_{len(selected_data)}.pcd"

        point_cloud = pypcd.PointCloud.from_array(selected_data)
        point_cloud.save(f"{DATA_LOCATION_PATH}{save_name}")



@dataclasses.dataclass
class ScriptSetting:
    stat_based: bool
    k_means: bool
    ml: bool
    filename: str