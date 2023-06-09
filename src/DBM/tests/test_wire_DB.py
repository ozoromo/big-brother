import sys
import unittest
import uuid
sys.path.append("..")

from parameterized import parameterized
import mongomock
from PIL import Image
import numpy as np

from DatabaseManagement import wire_DB

class WireDBTest(unittest.TestCase):
    def output_assertEqual(self, check, expected):
        self.assertEqual(check, expected, 
                         f"Expected {expected}, but {check} found.")

    def setUp(self):
        client = mongomock.MongoClient()
        self.db = wire_DB(mongo_client=client)
    
    def test_insertTrainingPicture(self):
        # TODO: Put encoding into the registration
        user_ids = [self.db.register_user("sylphid", None),
                   self.db.register_user("number", None),]
        
        img_sylphid = []
        img_np_sylphid = []
        pic_id_sylphid = []
        for i in range(3):
            img = Image.open(f"images/sylphid{i}.jpg")
            img_np = np.asarray(img, dtype=np.float64)
            pic_id = self.db.insertTrainingPicture(
                    np.asarray(img, dtype=np.float64), user_id
                )

        # convert back
        pilImage = Image.fromarray(img_np.astype('uint8'))
        pilImage.save("test.jpg")

if __name__ == "__main__":
    unittest.main()
