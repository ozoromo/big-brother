import sys
import unittest
import uuid
sys.path.append("..")

from parameterized import parameterized
import mongomock
from PIL import Image
import numpy as np

from DatabaseManagement import wire_DB, UserDoesntExist

class WireDBTest(unittest.TestCase):
    def output_assertEqual(self, check, expected):
        self.assertEqual(check, expected, 
                         f"Expected {expected}, but {check} found.")

    def setUp(self):
        client = mongomock.MongoClient()
        self.db = wire_DB(mongo_client=client)
    
    def test_basic_insertion_and_retrieval_training_pic(self):
        # TODO: Put encoding into the registration
        user_ids = [self.db.register_user("sylphid", None),
                   self.db.register_user("number", None),]
        
        img_sylphid = []
        img_np_sylphid = []
        pic_id_sylphid = []
        for i in range(3):
            img = Image.open(f"images/sylphid{i}.jpg")
            img_np = np.asarray(img, dtype=np.float64)
            img_np_sylphid.append(img_np)

            pic_id = self.db.insertTrainingPicture(img_np, user_ids[0])
            pic_id_sylphid.append(pic_id)

        # compare np-arrays
        pics, ids = self.db.getTrainingPictures(user_ids[0])
        for i in range(3):
            idx_pic = ids.index(pic_id_sylphid[i])
            self.assertTrue(np.allclose(img_np_sylphid[i], pics[idx_pic]))

    def test_user_deletion_and_associated_resources(self):
        self.assertRaises(UserDoesntExist, self.db.getTrainingPictures,
                          uuid.uuid1())

    def test_insertion_for_non_existing_user(self):
        self.assertRaises(UserDoesntExist, self.db.insertTrainingPicture,
                          np.array([1,2,3]), uuid.uuid1())
        self.assertRaises(UserDoesntExist, self.db.insertTrainingPicture,
                          np.array([[1,2,3],[12,3,3]]), uuid.uuid4())
    
    def test_insertion_of_non_existing_picture(self):
        user_ids = [self.db.register_user("sylphid", None),
                   self.db.register_user("number", None),]
        
        self.assertRaises(TypeError, self.db.insertTrainingPicture,
                          None, user_ids[0])
        self.assertRaises(TypeError, self.db.insertTrainingPicture,
                          None, user_ids[1])

if __name__ == "__main__":
    unittest.main()
