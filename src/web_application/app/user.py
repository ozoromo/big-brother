"""
TODO: Add a description of the module
"""

import io
import uuid
import base64

import numpy as np
from flask_login import UserMixin
from PIL import Image


class BigBrotherUser(UserMixin):
    """
    This class keeps the information about the user.
    """

    def __init__(self, user_uuid: uuid.UUID, name: str, DB):
        """
        Exceptions:
        TypeError -- Gets raised if the arguments are of the wrong type.
        """
        if type(user_uuid) != uuid.UUID:
            raise TypeError

        self.uuid = user_uuid
        self.name = name
        self.DB = DB

        self.trainingPictures = []
        """ logData: Used for logs. Stores past login dates as well as
        the picture IDs that are associated with those logins that came
        from the user with the uuid: self.uuid """
        self.logData = []
        self.trainingPicturesWebsiteFormat = []

        self.admin = False
        self.childUser = []

        self.sync()

        self.recogFlag = False

    def sync(self):
        pics, uuids = self.DB.get_pictures(user_uuid=self.uuid)
        self.trainingPicturesWebsiteFormat = []

        for pic_index, pic in enumerate(pics):
            try:
                file_object = io.BytesIO()
                img = Image.fromarray(pic.astype('uint8'))
                img.save(file_object, 'PNG')
                base64img = "data:image/png;base64," + base64.b64encode(file_object.getvalue()).decode('ascii')
                self.trainingPicturesWebsiteFormat.append((uuids[pic_index], base64img))
            except ValueError:
                print("ValueError: Illegal Image Loaded!")
                return

        self.logData = self.DB.get_login_log_of_user(user_uuid=self.uuid)
        # TODO: Setting permissions for admin?
        """
        admin_collection = self.DB['admin_table']
        query = {"admin_uuid": str(self.uuid)}
        result = admin_collection.find(query)

        self.childUser = []
        for document in result:
            child_user = document['child_user']
            self.admin = True
            self.childUser.append(child_user)
        """
        # TODO: What is this supposed to do? Is it ther to build some sort of
        # hierarchy?
        self.childUser = []

    def get_id(self):
        return self.uuid
    