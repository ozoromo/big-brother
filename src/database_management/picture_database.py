import os
import sys
import uuid
import datetime as dt
import typing

import numpy as np
import pickle
from pytz import timezone
import pymongo

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from database_management.base_database import BaseDatabase
from database_management.exceptions import UserDoesntExistException

class PictureDatabase(BaseDatabase):
    """
    This database stores pictures. This is specifically made in order to manage
    storing and getting pictures from the database.
    """

    def __init__(self, mongo_client=None):
        BaseDatabase.__init__(self, mongo_client=mongo_client)
        if not self._resource_context.find_one({"name": "wire"}):
            for _ in range(self._RETRY_AFTER_FAILURE):
                try: 
                    self._resource_context.insert_one({
                        "_id": str(uuid.uuid4()),
                        "name": "wire",
                        "username": None,
                        "res_id": []})
                    break
                except pymongo.errors.DuplicateKeyError:
                    pass

    def get_pictures(self, user_uuid: typing.Optional[uuid.UUID] = None):
        """
        Returns training pictures from the database from the wire resource context
        """
        if not self.check_user_id_exists(user_uuid):
            raise UserDoesntExistException("The user doesn't exist.")

        wire_context_collection = self._resource_context.find_one({"name": "wire"})
        assert(wire_context_collection is not None)

        resources = None
        if user_uuid: 
            resources = self._resource.find({
                        "_id": {"$in": wire_context_collection["res_id"]},
                        "user_id": str(user_uuid),
                    })
        else: 
            resources = self._resource.find({
                        "_id": {"$in": wire_context_collection["res_id"]},
                    })

        pics = []
        ids = []
        for r in resources:
            pics.append(pickle.loads(r["res"]))
            ids.append(uuid.UUID(r["_id"]))

        return pics, ids
    
    def insert_picture(self, pic: np.ndarray, user_uuid: uuid.UUID):
        """
        Inserts a new training picture into the database and returns the
        uuid of the inserted picture.

        Arguments:
        pic -- Picture to be inserted into the database.
        user_uuid -- ID of the user which owns the picture.

        Return:
        Returns the uuid of the picture that has been inserted into the database.

        Exception:
        TypeError -- Gets risen if the type of the input isn't the expected type.
        """
        if type(pic) != np.ndarray or type(user_uuid) != uuid.UUID:
            raise TypeError
        if not self.check_user_id_exists(user_uuid):
            raise UserDoesntExistException("The user doesn't exist.")
        
        pic_uuid = uuid.uuid4()
        for _ in range(self._RETRY_AFTER_FAILURE):
            try: 
                self._resource.insert_one({
                    "_id" : str(pic_uuid),
                    "user_id": str(user_uuid),
                    "res" : pickle.dumps(pic),
                    "date": dt.datetime.now(tz=timezone('Europe/Amsterdam')),
                })
                break
            except pymongo.errors.DuplicateKeyError:
                pic_uuid = uuid.uuid4()

        # TODO: Are there also exceptions that need to be handled?
        self._resource_context.update_one(
                {"name": "wire"},
                {"$addToSet": {"res_id": str(pic_uuid)}})

        return pic_uuid
