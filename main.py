import os
from pathlib import Path
import smtplib as eml

from pprint import pprint

from sparta_helper import Helper

path = Path(Path(os.path.abspath(__file__)).parent, 'source_data') ##
helper = Helper.new_school_year(path)
helper.resolve_missing_st_id()
helper.read_emails_from_csv(Path(path.parent, 'student_emails_(secrets).csv')) ##

