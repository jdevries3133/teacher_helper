from abc import ABC
from pathlib import Path


class BaseCsvParser(ABC):
    def __init__(self, csv_dir: Path):
        assert isinstance(csv_dir, Path)
        self.csv_dir = csv_dir


