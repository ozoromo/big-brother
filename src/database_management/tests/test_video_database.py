import sys
import os
import unittest
import uuid

from parameterized import parameterized
import mongomock
from mongomock.gridfs import enable_gridfs_integration
from PIL import Image
import numpy as np
import cv2

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from database_management.video_database import VideoDatabase
from database_management.exceptions import UserDoesntExistException

class VidDBTest(unittest.TestCase):
    def output_assertEqual(self, check, expected):
        self.assertEqual(check, expected, 
                         f"Expected {expected}, but {check} found.")

    def setUp(self):
        client = mongomock.MongoClient(connectTimeoutMS=30000,
                                       socketTimeoutMS=None,
                                       connect=False,
                                       maxPoolsize=1)
        self.db = VideoDatabase(client)
        enable_gridfs_integration()

    def test_video_insertion_non_existent_user(self):
        source = "videos/Program in C Song.mp4"
        compare = "tmp/test.mp4"

        self.db.register_user("me0", None)
        self.db.register_user("me1", None)
        self.db.register_user("me2", None)

        stream_insert = open(source, "rb+")
        self.assertRaises(UserDoesntExistException, 
                          self.db.insert_video, 
                          stream_insert, uuid.uuid1(), "", "")
        stream_insert.close()

    def test_video_insertion_and_retrival(self):
        source = "videos/Program in C Song.mp4"
        compare = "tmp/test.mp4"
        filename = "file"
        video_transcript = "Some transcript"

        user_id = self.db.register_user("me", None)

        stream_insert = open(source, "rb+")
        vid_uuid = self.db.insert_video(
                stream_insert, 
                user_id, 
                filename, 
                video_transcript
            )
        stream_insert.close()

        stream_out = open(compare, "wb+")
        ret_id, ret_fn, ret_transc = self.db.get_video_stream(vid_uuid, stream_out)
        stream_out.close()

        self.assertEqual(user_id, ret_id)
        self.assertEqual(filename, ret_fn)
        self.assertEqual(video_transcript, ret_transc)
        with open(source, "rb+") as f1, open(compare, "rb+") as f2:
            for l1, l2 in zip(f1, f2):
                self.assertTrue(l1 == l2)

    def test_retrival_non_existing_video(self):
        pass

    def test_retrieval_vid_ids_from_certain_user(self):
        source = "videos/Program in C Song.mp4"
        filename = "file"
        video_transcript = "Some transcript"

        user_id = self.db.register_user(f"me", None)

        vid_ids = []
        for i in range(10):
            stream_insert = open(source, "rb+")
            vid_uuid = self.db.insert_video(
                    stream_insert, 
                    user_id, 
                    filename, 
                    video_transcript
                )
            stream_insert.close()
            vid_ids.append(vid_uuid)

        ret_vid_ids = self.db.get_video_id_of_user(user_id)

        # testing equality
        vid_ids.sort()
        ret_vid_ids.sort()
        self.assertEqual(vid_ids, ret_vid_ids)

    def test_basic_video_deletion(self):
        """
        Tests whether videos with a certain ID can be deleted.
        """
        source = "videos/Program in C Song.mp4"

        filename = "file"
        video_transcript = "Some transcript"
        num_vid_to_test = 10
        vid_ids = []

        # inserting videos
        user_id = self.db.register_user(f"me", None)
        for i in range(num_vid_to_test):
            stream_insert = open(source, "rb+")
            vid_uuid = self.db.insert_video(
                    stream_insert,
                    user_id, 
                    filename, 
                    video_transcript
                )
            stream_insert.close()
            vid_ids.append(vid_uuid)
        vid_ids.sort()

        # deleting videos
        for _ in range(num_vid_to_test):
            vid_to_delete = vid_ids.pop()
            self.assertTrue(self.db.delete_video(vid_to_delete))

            # compare
            ret_vid_ids = self.db.get_video_id_of_user(user_id)
            ret_vid_ids.sort()
            self.assertEqual(vid_ids, ret_vid_ids)

if __name__ == "__main__":
    unittest.main()
