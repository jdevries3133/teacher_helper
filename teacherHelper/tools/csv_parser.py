class IterCsvException(Exception): ...


class IterCsv:
    def __init__(self, acceptable_headers, rows, strict=True, strip_data=True):
        """
        Generator returns context, and row. Context is a dict in which
        the key is one of the acceptable headers, and the value is the
        index at which that header field can be found in each row.
        """
        self.current_row = 0
        self.rows = rows
        self.context = {}
        self._acceptable_headers = acceptable_headers
        self._strict = strict
        self._strip_data = strip_data
        self._assign_context()

    def _assign_context(self):
        """Context is a mapping of header labels to row indices, so that the
        row items can later be fetched by name."""
        for i, raw_header in enumerate(self.rows[0]):
            raw_header = raw_header.lower()
            for clean_header in self._acceptable_headers:
                if not self._strict and clean_header in raw_header or raw_header in clean_header:
                    before = len(self.context)
                    self.context[clean_header] = i
                    after = len(self.context)
                    if before == after:
                        raise Exception(
                            'Two headers matched the acceptable_header:\t'
                            + clean_header
                            + '\nIf raw header matching is to lenient, set strict=True'
                        )
                elif self._strict and clean_header == raw_header:
                    before = len(self.context)
                    self.context[clean_header] = i
                    after = len(self.context)
                    if before == after:
                        raise Exception(
                            'There are two or more headers with the value'
                            f'{raw_header}. Edit the csv to differentiate'
                            'between these columns to continue.'
                        )
        self._validate_context(self.context)

    def fetch(self, name: str):
        """Fetch an item from a row by name during iteration."""
        if (index := self.context.get(name)) is None:
            raise IterCsvException(f'{name} does not exist in csv context')
        value = self.rows[self.current_row][index]
        if self._strip_data:
            return value.strip()
        return value

    def __iter__(self):
        return self

    def __next__(self):
        self.current_row += 1
        if self.current_row < len(self.rows) - 1:
            return self.fetch
        raise StopIteration

    @ staticmethod
    def _validate_context(context):
        """Because this field is misspelled in OnCourse....."""
        is_parent_spreadsheet = 'guardian first name' in context
        is_header_misspelled = context.get('student resides with') is None

        if is_parent_spreadsheet and is_header_misspelled:
            raise IterCsvException(
                'Remember, "student resides with"  is misspelled in '
                'OnCourse. Fix it in the CSV you downloaded.'
            )
