import sys
import unittest
import uuid
#sys.path.append("..")

from parameterized import parameterized
import bson
import mongomock
import os
import numpy as np
import pickle
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from DatabaseManagement import BBDB,UsernameExists

class BBDBTest(unittest.TestCase):
    def output_assertEqual(self, check, expected):
        self.assertEqual(check, expected, 
                         f"Expected {expected}, but {check} found.")

    def setUp(self):
        client = mongomock.MongoClient()
        self.db = BBDB(mongo_client=client)
    
    @parameterized.expand([
        [
            "single_name", 
            ["user"],
            [np.array([])],
        ],
        [
            "multiple_normal_names", 
            ["User0", "Hello", "World", "AnotherName", "Meow", 
             "somestrangestring", "moreUsers", "user2",
             "siii", "AllowedName"],
            [
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
            ],
        ],
        [
            "multiple_names_special_not_only_alphanum", 
            ["!User0", "0Hello&", "1World!", "0with space", "??1with other?", 
             "raise NotImplementedError", "more$Users&", "*3(*)&&$%)@",
             "(100)", "*&strangeButAllowedN(ame"],
            [
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
                np.array([]),
            ],
        ],
    ])
    
    def test_register_user_different_users(self, name, 
                                           usernames: list, 
                                           user_enc_res: list):
        """
        Testing different usernames. 

        Following functions are tested:
        - register_user
        - getUser
        - getUsername
        - getUsers
        - getUserWithId
        """
        self.assertDictEqual(self.db.getUsers(), 
                             {}, 
                             "Dictionary is supposed to be emtpy")
        user_ids = []
        for user, enc in zip(usernames, user_enc_res):
            tmp = self.db.register_user(user, enc)
            user_ids.append(tmp)
            l = len(user_ids)

            self.assertEqual(len(self.db.getUsers()), l, 
                             "Amount of users isn't correct")
            self.assertEqual(len(self.db.getUsers(limit=l//2)), l//2, 
                             "Limit-Keyword from BBDB.getUsers might not be implemented correctly")
            self.output_assertEqual(
                    self.db.getUsers(), 
                    {user_ids[i]: usernames[i] for i in range(l)}
                )
        self.assertEqual(len(user_ids), len(set(user_ids)),
                         "User IDs are not unique.")
    
        for i in range(len(usernames)):
            self.output_assertEqual(self.db.getUserWithId(user_ids[i]), usernames[i])
            self.output_assertEqual(self.db.getUser(usernames[i]), user_ids[i])

        self.output_assertEqual(self.db.getUsername(user_ids[::2]), usernames[::2])
        self.output_assertEqual(self.db.getUsername(user_ids[::-2]), usernames[::-2])
        self.output_assertEqual(self.db.getUsername(user_ids[::-1]), usernames[::-1])
        self.output_assertEqual(self.db.getUsername(user_ids[::3]), usernames[::3])

    def test_registration_with_existing_username(self):
        """
        Test registration with existing username.
        """
        # TODO: User encoding ID ask again...
        self.db.register_user("name", None)
        self.assertRaises(UsernameExists, 
                          self.db.register_user, 
                          "name", None)

    def test_getters_no_users(self):
        """ 
        Tests getter functions when where are no users in the database. Or
        the users that you want to do not exist.

        Tests the following methods:
        - getUser
        - getUsername
        - getUsers
        - getUserWithId
        """
        self.output_assertEqual(self.db.getUser(str(uuid.uuid1())), None)
        self.output_assertEqual(
                self.db.getUsername([uuid.uuid1(), uuid.uuid1()]), 
                [None, None]
            )
        self.output_assertEqual(self.db.getUsers(), {})
        self.output_assertEqual(self.db.getUserWithId(uuid.uuid1()), None)
    
    def test_basic_login_workflow(self):
        # TODO: Maybe implement more tests like this
        user_id = self.db.register_user("user", None)

        timestamp = self.db.login_user(user_id)
        # The pic uuid is assumed to be correct 
        inserted_pic_uuid = uuid.uuid1()
        self.assertEqual(
                self.db.update_login(user_uuid=user_id,
                                     time=timestamp,
                                     inserted_pic_uuid=inserted_pic_uuid),
                inserted_pic_uuid)
        self.assertEqual(self.db.getLoginLogOfUser(user_id)[0][0],
                         timestamp)
    
    def test_basic_user_deletion(self):
        user_id = self.db.register_user("user", None)
        self.assertTrue(self.db.delUser(user_id))

    def test_deletion_non_existing_user(self):
        self.db.register_user("user1", None)
        self.db.register_user("user2", None)
        self.assertFalse(self.db.delUser(uuid.uuid1()))
    
    def test_duplicate_getUsers(self):
        user_ids = [
                self.db.register_user("user0", None),
                self.db.register_user("user1", None),
            ]
        self.output_assertEqual(
                self.db.getUsername([user_ids[0], user_ids[1], user_ids[0]]),
                ["user0", "user1", "user0"]
            )
    
    def test_get_user_enc(self):
        user_encoding = np.random.randn(10)
        user_id = self.db.register_user("user", user_encoding)

        # Test the get_user_enc method
        retrieved_user_enc = self.db.get_user_enc(user_id)
        self.assertTrue(np.array_equal(retrieved_user_enc, user_encoding))
    
    def test_update_user_enc(self):
        original_user_enc = np.random.randn(10)  # Replace with your user encoding logic
        updated_user_enc = np.random.randn(10)  # Replace with your updated user encoding logic

        user_id = self.db.register_user("user_2", original_user_enc)
        self.db.update_user_enc(user_id, updated_user_enc)
        retrieved_user_enc = self.db.get_user_enc(user_id)

        # Check if the retrieved user encoding matches the updated encoding
        self.assertTrue(np.array_equal(retrieved_user_enc, updated_user_enc))

    def test_register_user(self):
        username = "user_1"
        user_encoding = None

        # Test registering a new user
        new_user_id = self.db.register_user(username, user_encoding)

        # Check if the user exists in the database
        self.assertTrue(self.db.checkUserIDExists(new_user_id))
        self.assertEqual(self.db.getUsername([new_user_id]), [username])

        # Test registering a user with an existing username
        with self.assertRaises(UsernameExists):
            self.db.register_user(username, user_encoding)

if __name__ == "__main__":
    unittest.main()
