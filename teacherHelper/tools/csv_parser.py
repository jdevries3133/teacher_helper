from abc import ABC
from pathlib import Path


class BaseCsvParser(ABC):
    def __init__(self, csv_dir: Path):
        assert isinstance(csv_dir, Path)
        self.csv_dir = csv_dir


class IterCsv:
    def __init__(self, acceptable_headers, rows, strict=True):
        """
        Generator returns context, and row. Context is a dict in which
        the key is one of the acceptable headers, and the value is the
        index at which that header field can be found in each row.
        """
        self.current_row = 0
        self.rows = rows
        self.context = {}
        # assign context
        for i, raw_header in enumerate(rows[0]):
            raw_header = raw_header.lower()
            for clean_header in acceptable_headers:
                if not strict and clean_header in raw_header or raw_header in clean_header:
                    before = len(self.context)
                    self.context[clean_header] = i
                    after = len(self.context)
                    if before == after:
                        raise Exception(
                            'Two headers matched the acceptable_header:\t'
                            + clean_header
                            + '\nIf raw header matching is to lenient, set strict=True'
                        )
                elif strict and clean_header == raw_header:
                    before = len(self.context)
                    self.context[clean_header] = i
                    after = len(self.context)
                    if before == after:
                        raise Exception(
                            'There are two or more headers with the value'
                            f'{raw_header}. Edit the csv to differentiate'
                            'between these columns to continue.'
                        )

    def __iter__(self):
        return self

    def __next__(self):
        self.current_row += 1
        if self.current_row < len(self.rows) - 1:
            return self.context, self.rows[self.current_row]
        raise StopIteration
