from difflib import ndiff


# TODO: remove me. This is just a worse version of csv.DictReader
class IterCsv:
    def __init__(self, acceptable_headers, rows, strip_data=True):
        """Generator returns context, and row. Context is a dict in which
        the key is one of the acceptable headers, and the value is the
        index at which that header field can be found in each row."""
        self.current_row = 0
        self.rows = rows
        self.context = {}
        self._acceptable_headers = acceptable_headers
        self._strip_data = strip_data
        self._assign_context()

    def _assign_context(self):
        """Context is a mapping of header labels to row indices, so that the
        row items can later be fetched by name."""
        for i, raw_header in enumerate(self.rows[0]):
            raw_header = raw_header.lower()
            for clean_header in self._acceptable_headers:
                if clean_header == raw_header:
                    # create mapping and check for duplicate match
                    before = len(self.context)
                    self.context[clean_header] = i
                    after = len(self.context)
                    if before == after:
                        raise ValueError(
                            "There are two or more headers with the value "
                            f"{raw_header}. Edit the csv to differentiate "
                            "between these columns to continue."
                        )
        if not (a := list(self.context.keys())) == (b := self._acceptable_headers):
            diff = "\n\t".join(ndiff(a, b))
            msg = "A match was not found for all headers:\n" f"DIFF:\n\t{diff}"
            raise ValueError(msg)
        self._validate_context(self.context)

    def fetch(self, name: str):
        """Fetch an item from a row by name during iteration."""
        if (index := self.context.get(name)) is None:
            raise ValueError(f"{name} does not exist in csv context")
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

    @staticmethod
    def _validate_context(context):
        """Because this field is misspelled in OnCourse....."""
        is_parent_spreadsheet = "guardian first name" in context
        is_header_misspelled = context.get("student resides with") is None

        if is_parent_spreadsheet and is_header_misspelled:
            raise ValueError(
                'Remember, "student resides with"  is misspelled in '
                "OnCourse. Fix it in the CSV you downloaded."
            )
