import csv
from datetime import datetime
import os
import re
import shelve

from student import Student

class Homeroom:
    def __init__(self, csv_path, csv_filename):
        """
        Ensure that string constants for csv headers of id, student names, and
        (if applicable) student emails are correct.
        """

