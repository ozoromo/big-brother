import os
import uuid
import datetime as dt
import typing
from dotenv import load_dotenv
import numpy as np
import pickle
from pytz import timezone
import pymongo

from database_management.exceptions import UserDoesntExistException, UsernameExistsException, ScriptExistException, ScriptSearchError, ScriptCreateError


class BaseDatabase:
    """Database Baseclass"""
    def __init__(self, mongo_client=None):
        """
        Builds up the initial connection to the database

        Optional Arguments:
        mongo_client -- In case you are using a different mongo cluster.
        We also offer a default mongo cluster that you can use. In case you
        use a different cluster with pre-existing information it has to have
        the same structure as specified in the documentation.

        """
        # load environment variables from .env-file 
        load_dotenv()
        
        if not mongo_client:
            new_mongo = "mongodb+srv://User:Hello@cluster0.rd6xjc9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
            self.cluster = pymongo.MongoClient(new_mongo,
                                               connectTimeoutMS=30000,
                                               socketTimeoutMS=None,
                                               connect=False,
                                               maxPoolsize=1)
        else:
            self.cluster = mongo_client

        # Constants
        self._RETRY_AFTER_FAILURE = 10

        # Values
        self._db = self.cluster["BigBrother"]
        self._user = self._db["user"]
        self._login_attempt = self._db["login_attempt"]
        self._resource = self._db["resource"]
        self._resource_context = self._db["resource_context"]
        self._lua_scripts = self._db["lua_scripts"]

    def close(self):
        """
        Close the connection with the database
        """
        self.cluster.close()

    def delete_user(self, user_id: uuid.UUID) -> bool:
        """
        Delete a user from the database.

        Arguments:
        user_id -- ID of the user that you want to delete.

        Return:
        Returns True if the user has been deleted and False otherwise.
        """
        user_id = str(user_id)
        if self._user.find_one({"_id": user_id}):
            self._user.delete_one({"_id": user_id})
            return True
        print("WARNING: Database login failed while deleting user.")
        return False

    def add_admin_relation(self, user_id: uuid.UUID):
        """
        Add a user as an admin.

        Arguments:
        user_id -- ID of the user you want to add to add as admin

        Return:
        Returns True if the user has been added and False otherwise.
        """
        user_id = str(user_id)
        if self._user.find_one({"_id": user_id}):
            self._user.update_one({"_id": user_id}, {"$set": {"is_admin": True}})
            return True
        print("WARNING: AddAdminRelation Failed!")
        return False

    def check_user_id_exists(self, uuid: typing.Optional[uuid.UUID]):
        """
        Checks whether a certain uuid already exists.

        Arguments:
        uuid -- The user id that you want to verify.

        Return:
        Returns True if the user id exists already and false if it doesn't
        exist.
        """
        for existing_uuid in self.get_users():
            if existing_uuid == uuid:
                return True
        return False

    def get_username(self, uuids: list):
        """
        Fetches usernames from database belonging to the given uuids

        Arguments:
        uuids -- This is a list of user_uuid. Those are the uuids of which you want to get the usernames.

        Return:
        Returns the a list of usernames that correspond to the user_uuid
        that have been inputted. The index i of the return list corresponds
        to uuids[i] in the input. It a uuid doesn't belong to any user then None
        is returned for the entry.
        """
        usernames = []
        for user_id in uuids:
            entries = self._user.find_one({"_id": str(user_id)})
            entry = None
            if entries:
                entry = entries["username"]
            usernames.append(entry)
        return usernames

    def login_user(self, user_id: uuid.UUID):
        """
        Creates a new entry in the login_table for the user with the given uuid or username.

        Arguments:
        user_id -- ID of the user that you are login in.

        Return:
        Returns (False, False) if the login fails and the timestamp of the
        login if it succeeds.
        """
        localTime = dt.datetime.now(tz=timezone('Europe/Amsterdam'))
        if self._user.find_one({"_id": str(user_id)}):
            self._login_attempt.insert_one({
                "user_id": str(user_id),
                "date": localTime,
                "login_suc": False,           # initially False; set to True if update_login() successfull
                "success_resp_type": None,    # initially None; set to int if update_login() successfull
                "success_res_id": None,       # initially None; set to uuid if update_login() successfull
            })
            return localTime
        print("WARNING: Database login failed while loggin in user.")
        return False, False

    def update_login(self, user_uuid: uuid.UUID, time: dt.datetime, success_res_uuid: typing.Optional[uuid.UUID]):
        """
        Updates the status of the login of one user with the given user_uuid

        Arguments:
        user_uuid -- ID of the user of which you want to log in.
        time -- The timestamp of the login you want to update.
        success_red_uuid -- the uuid for the res in the resource table.

        Return:
        Returns False if the access to the database hasn't been
        successful and returns the UUID (insert_pic_uuid) if the program
        has been successful.

        Exception:
        ValueError -- Raised if the types of the input is not correct.
        """
        if    (type(user_uuid) != uuid.UUID) \
           or (type(time) != dt.datetime) \
           or ((type(success_res_uuid) != uuid.UUID) and (success_res_uuid is not None)):
            raise ValueError

        try:
            self._login_attempt.update_one(
                {
                    "user_id": str(user_uuid),
                    "date": time
                },
                {
                    "$set": {
                        "login_suc": True,
                        "success_resp_type": 0,
                        "success_res_id": str(success_res_uuid),
                    }
                })
            return success_res_uuid
        except Exception:
            print("WARNING: Database login failed whiel updating login!")
            return False

    def get_login_log_of_user(self, user_uuid: uuid.UUID):
        """
        Outputs log data of the user.

        Arguments:
        user_uuid -- The id of the user from which you want to get the log
        data.

        Returns:
        A list containing multiple Lists with the following structure:
        [<login_date>, <res_id of success resource>]. If the a login at
        a certain date wasn't successful then the res_id will be None.
        """
        log = []
        logins = self._login_attempt.find({"user_id": str(user_uuid)})
        for login in logins:
            if not login["success_res_id"]:
                log.append([login["date"], login["success_res_id"]])
            else:
                log.append([login["date"], uuid.UUID(login["success_res_id"])])
        return log

    def register_user(self, username: str, user_enc: np.ndarray):
        """
        Creates a new user in the database with the given username.

        Arguments:
        username -- The username of the new user.
        user_enc -- encoding of the user.

        Return:
        If the user has been successfully registered then it returns the
        user_id of the user what has been created.

        Exception:
        Raises an exception if the username already exists.
        """
        if user_enc is None:
            user_enc = np.array([])
        if self._user.find_one({"username": username}):
            raise UsernameExistsException("Username in use!")

        new_uuid = uuid.uuid4()
        for _ in range(self._RETRY_AFTER_FAILURE):
            try:
                self._user.insert_one({
                    "_id": str(new_uuid),
                    "username": username,
                    "user_enc_res": None,
                    "is_admin": False})
                break
            except pymongo.errors.DuplicateKeyError:
                new_uuid = uuid.uuid4()

        self.update_user_enc(new_uuid, user_enc)
        return new_uuid

    def update_user_enc(self, user_uuid: uuid.UUID, user_enc: np.ndarray):
        """
        Updates the user encoding of a user.

        Arguments:
        user_uuid: id of the user.
        user_enc: The user encoding to update.

        Return:
        Returns True if the encoding has been update and False otherwise.

        Exception:
        Raises a TypeError if the inputted encoding isn't a numpy array and
        raises a UserDoesntExistException exception if the uuid doesn't belong to an
        existing user.
        """
        # TODO: Perhaps write some more tests for this functionality.
        if type(user_enc) != np.ndarray:
            raise TypeError
        if not self.check_user_id_exists(user_uuid):
            raise UserDoesntExistException("The user doesn't exist.")

        # TODO: Does it need to be stored with gridFS?
        self._user.update_one(
            {"_id": str(user_uuid)},
            {"$set": {"user_enc_res": pickle.dumps(user_enc)}}
        )
        return True

    def get_user_enc(self, user_uuid: uuid.UUID) -> np.ndarray:
        """
        Get the user encoding from a certain user.

        Arguments:
        user_uuid: The ID of the user.

        Return:
        Returns user encoding.

        Exception:
        Raises UserDoesntExistException exception if the user doesn't exist.
        """
        if not self.check_user_id_exists(user_uuid):
            raise UserDoesntExistException("The user doesn't exist.")

        resource = self._user.find_one({"_id": str(user_uuid)})
        return pickle.loads(resource["user_enc_res"])

    def get_users(self, limit=-1):
        """
        Fetches all Users with their uuids and usernames from the database

        Optional arguments:
        limit -- This argument sets the amount of users that you want to limit
        your request to. If it's set to a negative number (which it is by default),
        then the search isn't limited.

        Return:
        If `limit` is negative then it returns a dictionary of all users and the
        associated usernames. If the limit is non-negative then it returns a
        list with `limit` amount of entries. The dictionary key are the user_uuid
        (with type uuid.UUID) and the value is the username (with type str).
        """
        users = self._user.find()
        if limit == 0:
            return {}
        elif limit > 0:
            users = users.limit(limit)

        user_dict = {}
        for user in users:
            user_dict[uuid.UUID(user["_id"])] = user["username"]
        return user_dict

    def get_user_with_id(self, user_id: uuid.UUID) -> typing.Optional[str]:
        """
        Returns the username corresponding to the user_id.

        Arguments:
        user_id -- The user_id aka _id.

        Return:
        Returns the username corresponding to the user_id. If the user with the
        given ID doesn't exist then None gets returned.
        """
        user_entry = self._user.find_one({"_id": str(user_id)})
        if not user_entry:
            return None
        return user_entry["username"]

    def delete_user_with_id(self, user_id: uuid.UUID) -> bool:
        """
        Deletes the user with the given user_uuid from the database and all data cooresponding to it.

        Arguments:
        user_id: ID of the user that should be deleted.

        Return:
        Returns True if the user has been successfully deleted. And
        False otherwise (e.g. user didn't exist in the database).
        """
        user_id = str(user_id)
        if self._user.find_one({"_id": user_id}):
            self.delete_user(user_id)
            self._login_attempt.delete_many({"user_id": user_id})
            self._resource.delete_many({"user_id": user_id})
            # TODO: resource_context also needs to get updated
            return True
        return False

    def get_user(self, username: str) -> typing.Optional[uuid.UUID]:
        """
        Returns the uuid corresponding to the username.

        Arguments:
        username -- The username of the user.

        Return:
        Returns the uuid corresponding to the username. If the username
        doesn't exist then it returns None.
        """
        user_entry = self._user.find_one({"username": username})
        if not user_entry:
            return None
        return uuid.UUID(user_entry["_id"])

    def save_lua_script(self, user_id, script_name, script_content, is_private):
        if self._lua_scripts.find_one({"script_name": script_name}) :
            raise ScriptExistException("Script with same Name already exsists!")
        
        document = {
            'user_id': user_id,
            'script_name': script_name,
            'script_content': script_content,
            'is_private': is_private
        }
        
        try:
            self._lua_scripts.insert_one(document)
        except Exception as e:
            raise ScriptCreateError("An error occurred while adding the script to the Database")
        
        return script_name
    
    def get_accessible_scripts(self, user_id):
        query = {
            '$or': [
                {'user_id': str(user_id)},
                {'is_private': False}
            ]
        }
        
        try:
            scripts = list(self._lua_scripts.find(query))
        except Exception as e:
            raise ScriptSearchError("An error occured while searching for scripts")
        return [(script['script_name']) for script in scripts]
        
    def get_lua_script_by_id(self, script_name):
        try:
            script = self._lua_scripts.find_one({'script_name': script_name})
        except Exception as e:
            raise ScriptSearchError("Script not found")

        return script['script_content']