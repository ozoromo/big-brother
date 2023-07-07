import sys
import unittest
import uuid
sys.path.append("..")

from parameterized import parameterized
import mongomock
from mongomock.gridfs import enable_gridfs_integration
from PIL import Image
import numpy as np
import cv2

from DatabaseManagement import vid_DB, UserDoesntExist

class WireDBTest(unittest.TestCase):
    def output_assertEqual(self, check, expected):
        self.assertEqual(check, expected, 
                         f"Expected {expected}, but {check} found.")

    def setUp(self):
        client = mongomock.MongoClient(connectTimeoutMS=30000,
                                       socketTimeoutMS=None,
                                       connect=False,
                                       maxPoolsize=1)
        self.db = vid_DB(client)
        enable_gridfs_integration()

    def test_video_insertion_non_existent_user(self):
        source = "videos/Program in C Song.mp4"
        compare = "tmp/test.mp4"

        self.db.register_user("me0", None)
        self.db.register_user("me1", None)
        self.db.register_user("me2", None)

        stream_insert = open(source, "rb+")
        self.assertRaises(UserDoesntExist, 
                          self.db.insertVideo, 
                          stream_insert, uuid.uuid1())
        stream_insert.close()

    def test_video_insertion_and_retrival(self):
        source = "videos/Program in C Song.mp4"
        compare = "tmp/test.mp4"

        user_id = self.db.register_user("me", None)

        stream_insert = open(source, "rb+")
        vid_uuid = self.db.insertVideo(stream_insert, user_id)
        stream_insert.close()

        stream_out = open(compare, "wb+")
        self.db.getVideoStream(vid_uuid, stream_out)
        stream_out.close()

        with open(source, "rb+") as f1, open(compare, "rb+") as f2:
            for l1, l2 in zip(f1, f2):
                self.assertTrue(l1 == l2)

if __name__ == "__main__":
    unittest.main()
