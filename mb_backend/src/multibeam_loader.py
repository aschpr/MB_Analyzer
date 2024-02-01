from typing import Generator, Any, Mapping
import utm
import dataclasses



@dataclasses.dataclass
class MBEntry:
    """
    Dataclass for a single multibeam entry
    """
    easting: float
    northing: float
    h_depth: float
    zone_number: int
    zone_letter: str
    chunk_index: str


class MBLoader:
    """
    Class for loading multibeam data
    """

    def __init__(self, file_path: str, to_utm: bool = True, separator: str = ","):
        self.file_path: str = file_path
        self.to_utm: bool = to_utm
        self.separator: str = separator

    def load_data_generator(self, stop: int = None) -> Generator[MBEntry, None, None]:
        """
        Load the data row by row
        data_spec = 16.004316488710927,-47.90545880409822,-4018.128
        :return:
        """

        with open(self.file_path, "r", encoding='utf-8') as f:
            current_index: int = 0

            for line in f:
                current_index += 1
                if stop is not None and current_index > stop:
                    break

                # print every 1000 lines
                if current_index % 100_000 == 0:
                    print(f"Loaded {current_index} lines")

                if self.to_utm:
                    values = [float(x) for x in line.split(self.separator)]
                    data_utm = utm.from_latlon(values[0], values[1])
                    yield MBEntry(data_utm[0],
                                  data_utm[1],
                                  values[2],
                                  data_utm[2],
                                  data_utm[3],
                                  "")
                else:
                    yield line.split(self.separator)
