import sys
import os
import unittest
import uuid

from parameterized import parameterized
import mongomock
from PIL import Image
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from database_management.picture_database import PictureDatabase
from database_management.exceptions import UserDoesntExistException

class PictureDatabaseTest(unittest.TestCase):
    def output_assertEqual(self, check, expected):
        self.assertEqual(check, expected, 
                         f"Expected {expected}, but {check} found.")

    def setUp(self):
        client = mongomock.MongoClient()
        self.db = PictureDatabase(mongo_client=client)
    
    def test_basic_insertion_and_retrieval_pic(self):
        user_ids = [self.db.register_user("sylphid", None),
                   self.db.register_user("number", None),]
        
        img_sylphid = []
        img_np_sylphid = []
        pic_id_sylphid = []
        for i in range(3):
            img = Image.open(f"images/sylphid{i}.jpg")
            img_np = np.asarray(img, dtype=np.float64)
            img_np_sylphid.append(img_np)

            pic_id = self.db.insert_picture(img_np, user_ids[0])
            pic_id_sylphid.append(pic_id)

        # compare np-arrays
        pics, ids = self.db.get_pictures(user_ids[0])
        for i in range(3):
            idx_pic = ids.index(pic_id_sylphid[i])
            self.assertTrue(np.allclose(img_np_sylphid[i], pics[idx_pic]))

    def test_user_deletion_and_associated_resources(self):
        self.assertRaises(UserDoesntExistException, self.db.get_pictures,
                          uuid.uuid1())

    def test_insertion_for_non_existing_user(self):
        self.assertRaises(UserDoesntExistException, self.db.insert_picture,
                          np.array([1,2,3]), uuid.uuid1())
        self.assertRaises(UserDoesntExistException, self.db.insert_picture,
                          np.array([[1,2,3],[12,3,3]]), uuid.uuid4())
    
    def test_insertion_of_non_existing_picture(self):
        user_ids = [self.db.register_user("sylphid", None),
                   self.db.register_user("number", None),]
        
        self.assertRaises(TypeError, self.db.insert_picture,
                          None, user_ids[0])
        self.assertRaises(TypeError, self.db.insert_picture,
                          None, user_ids[1])

if __name__ == "__main__":
    unittest.main()
