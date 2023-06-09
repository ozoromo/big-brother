import sys
import unittest
import uuid
sys.path.append("..")

from parameterized import parameterized
import mongomock
from PIL import Image
import numpy as np
import cv2

from DatabaseManagement import vid_DB

class WireDBTest(unittest.TestCase):
    def output_assertEqual(self, check, expected):
        self.assertEqual(check, expected, 
                         f"Expected {expected}, but {check} found.")

    def setUp(self):
        client = mongomock.MongoClient()
        self.db = vid_DB(client)

    def test_video_insertion_and_retrival(self):
        source = "videos/Program in C Song.mp4"
        compare = "tmp/test.mp4"

        stream_insert = open(source, "rb+")
        vid_uuid = self.db.insertVideo(stream_insert, uuid.uuid1())
        stream_insert.close()

        stream_out = open(compare, "wb+")
        self.db.getVideoStream(vid_uuid, stream_out)
        stream_out.close()

        with open(source, "rb+") as f1, open(compare, "rb+") as f2:
            for l1, l2 in zip(f1, f2):
                self.assertTrue(l1 == l2)

if __name__ == "__main__":
    unittest.main()
