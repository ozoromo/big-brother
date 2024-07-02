import os
import sys
import uuid
import datetime as dt
import typing
import gridfs

import numpy as np
import pickle
from pytz import timezone
import pymongo
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from database_management.base_database import BaseDatabase
from database_management.exceptions import UserDoesntExistException

class ScriptDatabase(BaseDatabase):
    """
    This database stores lua scripts
    """

    def __init__(self,dbhost=None):
        BaseDatabase.__init__(self, dbhost)
        self._scripts = self._db["scripts"]
        self.fs = gridfs.GridFSBucket(self._db, bucket_name="scripts")

    def save_script(self, script_name, file_path):
        """
        Saves a script in the database
        """
        
        with open(file_path, 'rb') as file:
            self.fs.upload_from_stream(script_name, file)
        return 

    def get_script(self, script_name, output_file_path):
        """
        Retrieves a script from the database
        """

        with open(output_file_path, "wb") as output_file:
            self.fs.download_to_stream_by_name(script_name, output_file)


if __name__ == "__main__":
    
    db = ScriptDatabase()


    ########### Test save and get script ###########
    
    filepath = "src/database_management/tests/test.py"
    name = "neuerTest"

    db.save_script(name, filepath)
    db.get_script(name, "src/database_management/tests/testRetrieve.py")