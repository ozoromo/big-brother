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
        self._VIDEO_RESOURCE_BUCKET_FILES = "vid_resource.files"

    def insert_video(self, vid, user_uuid: uuid.UUID, filename: str, kursID: str, video_transcript=""):
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
                    str(user_uuid), # filename but doesnt make much sense to set user_uuid as filename
                    source = vid,
                    metadata = {
                        "vid_id": vid_uuid,
                        "user_id": str(user_uuid),
                        "course_id": kursID,
                        "date": dt.datetime.now(tz=timezone('Europe/Amsterdam')),
                        "filename": filename,
                        "video_transcript": video_transcript
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
    
    # default values for download and path, path is set just for testing
    def get_videos_of_course(self,kurs_id, download=False, video_download_path="video_dir\TESTS\Marketing" ): 
        video_infos = []
        fs = GridFSBucket(self._db, self._VIDEO_RESOURCE_BUCKET)
        for gridout in fs.find({"metadata.course_id": kurs_id}):
            print(gridout)
            video_infos.append(gridout)
        
        if download: 
            if not os.path.exists(video_download_path):
                os.makedirs(video_download_path)
        
            for video in video_infos:  
                name = f"{video.metadata['filename']}"
                output_path = os.path.join(video_download_path, f"{name}.mp4")
                with open(output_path, 'wb') as path:
                        self.get_video_stream(uuid.UUID(video._id), path)
        
        return video_infos
    
    def insert_multiple_videos_from_path(self, courses_path): 
        video_ids = []
        for course in courses_path: 
            for video_in_course_folder in os.listdir(f"video_dir\Marketing\{course}"):
                for video_in_folder in os.listdir(f"video_dir\Marketing\{course}\{video_in_course_folder}"):
                    video_path = f"video_dir\Marketing\{course}"
                    with open(f"{video_path}\{video_in_course_folder}\{video_in_folder}", 'rb') as video_file:
                        vid_uuid = db.insert_video(video_file, user_uuid, filename=video_in_course_folder, kursID=course)
                        video_ids.append(vid_uuid)
        return video_ids
    
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


#### JUST FOR TESTING; DELETE IF PUSHING TO SERVER ####
if __name__ == "__main__":
    import io
    import uuid

    db = VideoDatabase()
    user_uuid = uuid.UUID("98513bb1-45a1-4cf4-805e-be38f64e2d18") # Test user in DB
    # vid = io.BytesIO(b"Hello World")
    video_path = "video_dir\\Marketing\\37922\\video_1\\video_1.mp4"
    courses = os.listdir("video_dir\Marketing")



    kurs_id = '37922'
    videos = db.get_videos_of_course(kurs_id=kurs_id, download=True)

    for video in videos:
        print(video)

    vid_id_of_user = db.get_video_id_of_user(user_uuid)
    print(vid_id_of_user)
    