import os
import sys
import time
import queue
import uuid
import typing

import numpy as np
import cv2

from app.user import BigBrotherUser
from app import picture_database


class UserManager:
    """
    This class manages the users of the websites.

    It manages the user and keeps information about them that needs to get
    accessed in other conponents of the frontend. This is used with the
    login maanger of flask in order to keep track of sessions.
    """
    def __init__(self):
        # Keeps track of the users and their session keys
        self.BigBrotherUserList = []
        userDict = picture_database.get_users().items()
        for key, value in picture_database.get_users().items():
            self.BigBrotherUserList.append(BigBrotherUser(key, value, picture_database))

    def get_user_by_id(self, user_uuid: uuid.UUID) -> typing.Optional[BigBrotherUser]:
        """
        Searches and returns the a user with a certain id.

        Arguments:
        user_uuid -- The ID of the user that you are trying to search.

        Return:
        Returns the user with the give ID. Returns None if the user
        with the ID doesn't exist.

        Exception:
        TypeError -- Gets risen if the type of the arguments is incorrect.
        """
        if type(user_uuid) != uuid.UUID:
            raise TypeError

        # TODO: Implement a more efficient way of searching
        for user in self.BigBrotherUserList:
            if user.uuid == user_uuid:
                return user
        return None
