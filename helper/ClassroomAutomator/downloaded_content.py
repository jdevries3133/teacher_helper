from pathlib import Path

from ..docx_utils import regex_search

class DownloadedContent:
    """
    This mixin acts on directories of content downloaded from google classroom.
    For example, nested word documents or google classroom JSON objects exported
    through Google Takeout.
    """
    def __init__(self, directory):
        if not isinstance(directory, Path):
            raise ValueError('Directory must be pathlib path object.')
        self.directory = directory
        pass

    def get_regex_classroom_doc(self, regex, yes=False, bad_link_regex=r''):
        """
        Iterate through a list of word documents downloaded from google classroom.
        The assumption is that docs will follow the naming convention where the student's
        full name is the start of the filename, followed by a dash.

        Optionally, it can also take a bad link regex which will pull out bad links,
        so that you can follow up with students who pasted partial links.

        Returns a list of tuples of the student name paired with the regex match
        string or None.
        """
        matched_links = []
        bad_links = []
        for doc in self.path.iterdir():
            if doc.name[-4:] != 'docx':
                continue
            student_name = doc.name[:doc.name.index('-')-1]
            matches, misses = regex_search(st, doc, regex, near_match_regex=bad_link_regex)
            matched_links += [(match, student_name) for match in matches]
            if misses:
                bad_links += [(miss, student_name) for miss in misses]
        if bad_link_regex:
            return matched_links, bad_links
        return matched_links

    
    def from_classroom(self, regex, flag, attribute, classroom_path):
        """
        Utility function for getting assignment data or grades from google
        classrom json repository. Searches flag (assignments, posts, comments)
        for the regex, and assigns the value of the result to the student as
        whatever string is passed as atribute.

        classroom_path must be pathlib Path object
        """
        submissions = []
        for path in classroom_path.iterdir():
            with open(path, 'r') as jsn:
                obj = json.load(jsn)
            if flag == "assignment":
                for post in obj['posts']:
                    if 'courseWork' in post.keys():
                        mo = re.fullmatch(regex, post['courseWork']['title'])
                        if mo:
                            submissions += post['courseWork']['submissions']
        for submission in submissions:
            try:
                submitter = self.find_nearest_match([submission['student']['profile']['name']['fullName']])[0]
                submitter.__dict__.setdefault(attribute, submission)
                print(f'set attribute {attribute} on student {submitter.name} for submission\n{submission}\n\n')
            except IndexError:
                pass
        return 0