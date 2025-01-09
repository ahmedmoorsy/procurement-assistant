from pathlib import Path
import pandas as pd


class CSVDataExtractor:
    """
    Extract data from a CSV file in batches.
    """

    def __init__(self, csv_file: str, chunk_size: int = 10000):
        self.csv_file = Path(csv_file)
        self.chunk_size = chunk_size

    def extract_data(self):
        """
        Generator that yields pandas DataFrame chunks.
        """
        if not self.csv_file.exists():
            raise FileNotFoundError(f"File not found: {self.csv_file}")

        data_iter = pd.read_csv(self.csv_file, chunksize=self.chunk_size, dtype=str)
        for chunk in data_iter:
            yield chunk
