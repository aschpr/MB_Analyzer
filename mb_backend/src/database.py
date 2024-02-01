import dataclasses
import sqlite3
from sqlite3 import Connection
from typing import Mapping

from src.multibeam_loader import MBEntry


def _build_sql_for_dataset_table(table_name: str) -> str:
    return (f"    CREATE TABLE IF NOT EXISTS {table_name}"
            "    (id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "                            easting DOUBLE,"
            "                            northing DOUBLE,"
            "                            h_depth DOUBLE,"
            "                            zone_number INT,"
            "                            zone_letter VARCHAR(2),"
            "                            chunk_index DOUBLE)")


def _build_sql_insert_query(table_name: str) -> str:
    return (f"INSERT INTO {table_name} ("
            f"  easting, "
            f"  northing, "
            f"  h_depth, "
            f"  zone_number, "
            f"  zone_letter, "
            f"  chunk_index) "
            f"      VALUES (:easting, :northing, :h_depth, :zone_number, :zone_letter, :chunk_index)")


def _build_sql_select_query(table_name: str) -> str:
    return f"SELECT * FROM {table_name}"

class MBSQLDatabase:
    """
    This class is used to create a connection to a sqlite3 database.
    """

    def __init__(self, file_path: str):
        self.file_path: str = file_path

        self.connection: sqlite3.Connection = self._create_connection()
        self.cursor: sqlite3.Cursor = self.connection.cursor()

    def create_new_table(self, table_name: str):
        """
        Create a new table in the database
        :param table_name:
        :return:
        """
        self.cursor.execute(_build_sql_for_dataset_table(table_name))
        self.connection.commit()

    def insert_data(self, table_name: str, mb_data: list[MBEntry]):
        """
        Insert data into the database
        :param table_name:
        :param data:
        :return:
        """

        data: list[Mapping[str, float | int | str]] = []
        # convert dataclass to Mapping
        for entry in mb_data:
            data.append(dataclasses.asdict(entry))

        self.cursor.executemany(_build_sql_insert_query(table_name), data)
        self.connection.commit()

    def select_data(self, table_name: str) -> list[MBEntry]:
        """
        Select data from the database
        :param table_name:
        :return:
        """
        self.cursor.execute(_build_sql_select_query(table_name))
        data = self.cursor.fetchall()

        mb_data: list[MBEntry] = []
        for entry in data:
            mb_data.append(MBEntry(easting=entry[1],
                                   northing=entry[2],
                                   h_depth=entry[3],
                                   zone_number=entry[4],
                                   zone_letter=entry[5],
                                   chunk_index=entry[6]))

        return mb_data

    def _create_connection(self) -> Connection:
        """ create a database connection to a SQLite database """
        print(f"SQL VERSION: {sqlite3.version}")

        try:
            return sqlite3.connect(self.file_path)
        except sqlite3.Error as e:
            print(e)
            exit(1)

    def __del__(self):
        print("Closing connection to database")
        self.connection.close()

