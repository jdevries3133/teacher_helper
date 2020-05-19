import json
import os

from .helper import Helper

def import_gcapi_creds(path):
    """
    Path must point to json object containing google classroom api credentials.
    """

    from .classroom_api import GoogleClassroom

    with open(path) as jsn:
        creds = json.load(jsn)
        GoogleClassroom.credentials = creds


