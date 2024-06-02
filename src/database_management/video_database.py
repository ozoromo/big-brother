import os
import sys
import uuid
import datetime as dt
import typing

import numpy as np
import pickle
from pytz import timezone
from gridfs import GridFSBucket
import pymongo

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from database_management.base_database import BaseDatabase
from database_management.exceptions import UserDoesntExistException

class VideoDatabase(BaseDatabase):
    """
    This database stores videos. This is specifically made in order to manage
    storing and getting videos from the database.
    """

    def __init__(self,dbhost=None):
        BaseDatabase.__init__(self, dbhost)
        self._VIDEO_RESOURCE_BUCKET = "vid_resource"

    def insert_video(self, vid, user_uuid: uuid.UUID, filename: str, video_transcript: str):
        """
        Inserts a new video into the database and returns the 
        uuid of the inserted video.

        Arguments:
        vid -- The source stream of the video that is getting uploaded.
        This has to be a file-like object that implements `read()`. 
        Alternatively it's also allowed to be a string.
        user_uuid -- ID of the user that owns the video.
        filename -- Filename of the inserted data. The filename doesn't have to left empty
        video_transcript -- The transcript of the video.

        Return:
        Returns the uuid of the video that has been inserted into the database.

        Exception:
        TypeError -- Gets risen if the type of the input isn't the expected type.
        UserDoesntExistException -- Gets risen if the user doesn't exist.
        """
        if not self.check_user_id_exists(user_uuid):
            raise UserDoesntExistException("The user doesn't exist.")
        if type(user_uuid) != uuid.UUID or type(filename) != str \
           or type(video_transcript) != str:
           raise TypeError

        fs = GridFSBucket(self._db, self._VIDEO_RESOURCE_BUCKET)
        vid_uuid = str(uuid.uuid4())
        for i in range(self._RETRY_AFTER_FAILURE):
            try:
                fs.upload_from_stream_with_id(
                    vid_uuid,
                    str(user_uuid),
                    source = vid,
                    metadata = {
                        "vid_id": vid_uuid,
                        "user_id": str(user_uuid),
                        "date": dt.datetime.now(tz=timezone('Europe/Amsterdam')),
                        "filename": filename,
                        "video_transcript": video_transcript,
                    },
                )
                break
            # TODO: Are there more errors that should be handled?
            except pymongo.errors.DuplicateKeyError:
                vid_uuid = str(uuid.uuid4())
        
        self._resource_context.update_one(
            {"name": "video"},
            {"$addToSet": {"res_id": vid_uuid}}
        )
        return uuid.UUID(vid_uuid)        

    def get_video_stream(self, vid_uuid: uuid.UUID, stream):
        """
        Writes video with certain id into the stream.

        Arguments:
        vid_uuid: This is the id of the video that you want to get.
        stream -- The destination stream of the video that is getting downloaded.
        This has to be a file-like object that implements `write()`. 
        
        Return:
        Returns a list with [user_uuid, filename, video_transcript].

        Exception:
        TypeError -- Gets risen if the type of the input isn't the expected type.
        FileNotFoundError -- If the video with the id doesn't exist.
        """
        if type(vid_uuid) != uuid.UUID:
           raise TypeError

        fs = GridFSBucket(self._db, self._VIDEO_RESOURCE_BUCKET)
        fs.download_to_stream(str(vid_uuid), stream)
        
        user_uuid = filename = video_transcript = None
        # TODO: Is there some better way of avoiding errors with cursor?
        # peraps use exceptions with next operation
        for gridout in fs.find({"metadata.vid_id": str(vid_uuid)}):
            meta = gridout.metadata
            user_uuid = meta["user_id"]
            filename = meta["filename"]
            video_transcript = meta["video_transcript"]
            break
        if user_uuid is None:
            raise FileNotFoundError

        return [uuid.UUID(user_uuid), filename, video_transcript]

    def get_video_id_of_user(self, user_uuid: uuid.UUID) -> typing.List[uuid.UUID]:
        """
        Outputs list of video ids from videos that belong to a certain user.

        Arguments:
        user_uuid: This is the ID of the user from which you want to have the
        IDs of the video that belong to the user.
        
        Return:
        Returns a list of video IDs.

        Exception:
        TypeError -- Gets risen if the type of the input isn't the expected type.
        """
        if type(user_uuid) != uuid.UUID:
           raise TypeError

        fs = GridFSBucket(self._db, self._VIDEO_RESOURCE_BUCKET)
        
        vid_ids = []
        for gridout in fs.find({"metadata.user_id": str(user_uuid)}):
            meta = gridout.metadata
            vid_ids.append(uuid.UUID(meta["vid_id"]))
        return vid_ids

    def delete_video(self, vid_uuid: uuid.UUID) -> bool:
        """
        Deletes a video.

        Arguments:
        vid_uuid: ID of the video that you want to delete.
        
        Return:
        Returns True if the video has been deleted and false otherwise.

        Exception:
        TypeError -- Gets risen if the type of the input isn't the expected type.
        gridfs.errors.NoFile -- Gets risen if the video doesn't exist.
        """
        if type(vid_uuid) != uuid.UUID:
           raise TypeError

        fs = GridFSBucket(self._db, self._VIDEO_RESOURCE_BUCKET)
        fs.delete(str(vid_uuid))

        return True

    