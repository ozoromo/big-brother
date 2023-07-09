"""Big Brother Database Mangement Class

Manages Database Requests
can Import and Export Pictures from Database

@Author: Julian Flieller <@Dr.Hype#0001>
@Date:   2023-05-13
@Project: ODS-Praktikum-Big-Brother
@Filename: new_database_management.py
@Last modified by:   Julian Flieller
@Last modified time: 2023-06-16
"""
import numpy as np
import pickle
import uuid
import datetime as dt
from pytz import timezone
from gridfs import GridFSBucket
import pymongo
import typing


class BBDB:
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
        if not mongo_client:
            self.cluster = pymongo.MongoClient("mongodb+srv://admin:7EgqBof7tSUKlYBN@bigbrother.qse5xtp.mongodb.net/?retryWrites=true&w=majority",
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

    def close(self):
        """
        Close the connection with the database
        """
        self.cluster.close()
    
    def closeGraceful(self):
        """
        not needed for mongodb
        """
        self.close()

    def commit(self):
        """
        not needed for mongodb
        """
        return

    def delUser(self, user_id: uuid.UUID) -> bool:
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
        print("WARNING: Database Login Failed!")
        return False

    def addAdminRelation(self, user_id: uuid.UUID):
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

    def checkUserIDExists(self, uuid: typing.Optional[uuid.UUID]):
        """
        Checks whether a certain uuid already exists.

        Arguments: 
        uuid -- The user id that you want to verify.

        Return:
        Returns True if the user id exists already and false if it doesn't
        exist.
        """
        for existing_uuid in self.getUsers():
            if existing_uuid == uuid:
                return True
        return False

    def getUsername(self, uuids: list):
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
                "user_id" : str(user_id),
                "date" : localTime,
                "login_suc": False,           #initially False; set to True if update_login() successfull
                "success_resp_type": None,    #initially None; set to int if update_login() successfull
                "success_res_id": None,       #initially None; set to uuid if update_login() successfull
                })
            return localTime
        print("WARNING: Database Login Failed!")
        return False, False
        
    def update_login(self, **kwargs):
        """
        Updates the status of the login of one user with the given user_uuid

        Keyword arguments:
        user_uuid -- ID of the user of which you want to log in.
        time -- The timestamp of the login you want to update. 
        inserted_pic_uuid -- the uuid for the res in the resource table

        Return:
        Returns (False, False) if the access to the database hasn't been 
        successful and returns the UUID (insert_pic_uuid) if the program
        has been successful.
        """
        # TODO: Review this and the modules tha call this function
        user_id = time = inserted_pic_uuid = None
        
        for key, value in kwargs.items():
            if key == "user_uuid":
                user_id = value
            elif key == "time":
                time = value
            elif key == "inserted_pic_uuid":
                inserted_pic_uuid = value

            '''
            elif key == "success_res_id":
                success_res_id = value
            elif key == "success_resp_type":
                success_resp_type = value
            elif key == "res":
                res = value
            '''
        
        if not time or not inserted_pic_uuid or not user_id:
            print("WARNING: Database Login Failed!")
            return False, False
        
        try:
            self._login_attempt.update_one(
                {
                    "user_id": str(user_id),
                    "date": time
                },
                { 
                    "$set" : {
                        "login_suc": True,
                        "success_resp_type": 0,
                        "inserted_pic_uuid": str(inserted_pic_uuid),
                    }
                })
            return inserted_pic_uuid
        except Exception:
            print("WARNING: Database Login Update!")
            return False, False

    def getLoginLogOfUser(self, user_uuid: uuid.UUID):
        # TODO: Write tests for this method
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
            log.append([login["date"], login["success_res_id"]])
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
        if self._user.find_one({"username" : username}):
            raise UsernameExists("Username in use!")

        new_uuid = uuid.uuid4()
        for _ in range(self._RETRY_AFTER_FAILURE):
            try: 
                self._user.insert_one({
                    "_id": str(new_uuid),
                    "username" : username, 
                    "user_enc_res" : None,
                    "is_admin" : False})
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
        raises a UserDoesntExist exception if the uuid doesn't belong to an
        existing user.
        """
        # TODO: Perhaps write some more tests for this functionality.
        if type(user_enc) != np.ndarray:
            raise TypeError
        if not self.checkUserIDExists(user_uuid):
            raise UserDoesntExist("The user doesn't exist.")

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
        Raises UserDoesntExist exception if the user doesn't exist.
        """
        if not self.checkUserIDExists(user_uuid):
            raise UserDoesntExist("The user doesn't exist.")

        resource = self._user.find_one({"_id": str(user_uuid)})
        return pickle.loads(resource["user_enc_res"])

    def getUsers(self, limit=-1):
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

    def getUserWithId(self, user_id: uuid.UUID) -> typing.Optional[str]:
        """
        Returns the username corresponding to the user_id.

        Arguments:
        user_id -- The user_id aka _id.

        Return:  
        Returns the username corresponding to the user_id. If the user with the
        given ID doesn't exist then None gets returned.
        """
        user_entry = self._user.find_one({"_id" : str(user_id)})
        if not user_entry: 
            return None
        return user_entry["username"]

    def deleteUserWithId(self, user_id: uuid.UUID) -> bool:
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
            self.delUser(user_id)
            self._login_attempt.delete_many({"user_id": user_id}) 
            self._resource.delete_many({"user_id": user_id})
            # TODO: resource_context also needs to get updated
            return True
        return False

    def getUser(self, username: str) -> typing.Optional[uuid.UUID]:
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
    
    def getAllTrainingsImages(self):
        """
        This function has not been implemented.
        
        Returns all training images from the database in three lists: 
        pics, uuids, user_uuids
        """
        # TODO: Dicuss it's deletetion
        """
        pics,uuids,user_uuids=[],[],[]
        for pic in self.wire_train_pictures.find():
            pics.append(pickle.loads(pic["pic_data"]))
            uuids.append(pic["pic_uuid"])
            user_uuids.append(pic["user_uuid"])
        return pics, uuids, user_uuids
        """
        raise NotImplementedError

    def insertPicture(self, pic : np.ndarray, user_uuid : uuid.UUID):
        """
        This function has not been implemented.
        """
        # TODO: Take a look at what this funciton is supposed to do. 
        # Decide whether you want to implement it or not.

        # Returns True/False on Success or Error
        # Pickles Picture and inserts it into DB
        # pic : picture to be saved as np.ndarray
        # user_uuid : id of user wich owns picture

        # TODO: Error Handling, in the rare case that a duplicate
        # uuid is generated this method has to try again
        raise NotImplementedError

    def getPicture(self,query : str):
        """
        This function has not been implemented.
        """
        raise NotImplementedError

class wire_DB(BBDB):
    def __init__(self, mongo_client=None):
        BBDB.__init__(self, mongo_client=mongo_client)
        if not self._resource_context.find_one({"name": "wire"}):
            for _ in range(self._RETRY_AFTER_FAILURE):
                try: 
                    self._resource_context.insert_one({
                        "_id": str(uuid.uuid4()),
                        "name": "wire",
                        "username": None,
                        "res_id": []})
                    break
                except pymongo.errors.DuplicateKeyError:
                    pass

    def getTrainingPictures(self, user_uuid: typing.Optional[uuid.UUID] = None):
        """
        Returns training pictures from the database from the wire resource context
        """
        if not self.checkUserIDExists(user_uuid):
            raise UserDoesntExist("The user doesn't exist.")

        wire_context_collection = self._resource_context.find_one({"name": "wire"})
        assert(wire_context_collection is not None)

        resources = None
        if user_uuid: 
            resources = self._resource.find({
                        "_id": {"$in": wire_context_collection["res_id"]},
                        "user_id": str(user_uuid),
                    })
        else: 
            resources = self._resource.find({
                        "_id": {"$in": wire_context_collection["res_id"]},
                    })

        pics = []
        ids = []
        for r in resources:
            pics.append(pickle.loads(r["res"]))
            ids.append(uuid.UUID(r["_id"]))

        return pics, ids
    
    def insertTrainingPicture(self, pic: np.ndarray, user_uuid: uuid.UUID):
        """
        Inserts a new training picture into the database and returns the
        uuid of the inserted picture.

        Arguments:
        pic -- Picture to be inserted into the database.
        user_uuid -- ID of the user which owns the picture.

        Return:
        Returns the uuid of the picture that has been inserted into the database.

        Exception:
        TypeError -- Gets risen if the type of the input isn't the expected type.
        """
        if type(pic) != np.ndarray or type(user_uuid) != uuid.UUID:
            raise TypeError
        if not self.checkUserIDExists(user_uuid):
            raise UserDoesntExist("The user doesn't exist.")
        
        pic_uuid = uuid.uuid4()
        for _ in range(self._RETRY_AFTER_FAILURE):
            try: 
                self._resource.insert_one({
                    "_id" : str(pic_uuid),
                    "user_id": str(user_uuid),
                    "res" : pickle.dumps(pic),
                    "date": dt.datetime.now(tz=timezone('Europe/Amsterdam')),
                })
                break
            except pymongo.errors.DuplicateKeyError:
                pic_uuid = uuid.uuid4()

        # TODO: Are there also exceptions that need to be handled?
        self._resource_context.update_one(
                {"name": "wire"},
                {"$addToSet": {"res_id": str(pic_uuid)}})

        return pic_uuid

    def insertPicture(self, pic : np.ndarray, user_uuid : uuid.UUID):
        """
        This function has not been implemented.
        """
        # TODO: Take a look at what this funciton is supposed to do. 
        # Decide whether you want to implement it or not.

        # Returns True/False on Success or Error
        # Pickles Picture and inserts it into DB
        # pic : picture to be saved as np.ndarray
        # user_uuid : id of user wich owns picture
        # => Error Handling, in the rare case that a duplicate 
        # uuid is generated this method has to try again
        raise NotImplementedError

    def getPicture(self, query : str):
        """
        This function has not been implemented.
        """
        raise NotImplementedError


class vid_DB(BBDB):
    """Subclass from BBDB
    Inherits Methods and Variables"""

    def __init__(self,dbhost=None):
        BBDB.__init__(self, dbhost)
        self._VIDEO_RESOURCE_BUCKET = "vid_resource"

    def insertVideo(self, vid, user_uuid: uuid.UUID, filename: str, video_transcript: str):
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
        """
        if not self.checkUserIDExists(user_uuid):
            raise UserDoesntExist("The user doesn't exist.")
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

    def getVideoStream(self, vid_uuid: uuid.UUID, stream):
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

    def getVideoIDOfUser(self, user_uuid: uuid.UUID):
        if type(user_uuid) != uuid.UUID:
           raise TypeError

        fs = GridFSBucket(self._db, self._VIDEO_RESOURCE_BUCKET)
        
        vid_ids = []
        for gridout in fs.find({"metadata.user_id": str(user_uuid)}):
            meta = gridout.metadata
            vid_ids.append(uuid.UUID(meta["vid_id"]))
        return vid_ids

class opencv_DB(BBDB):
    def __init__(self):
        BBDB.__init__(self)


class frontend_DB(BBDB):
    def __init__(self):
        BBDB.__init__(self)


class UsernameExists(Exception):
    pass

class UserDoesntExist(Exception):
    pass

"""
# only for testing, remove in production
if __name__ == '__main__':
    #DB = BBDB()
    #DB.register_user("mike")
    #print(list(DB.user_table.find()))

    print("LMAO")
    #wireDB = wire_DB()
    #user = User.BigBrotherUser("0", "name", wireDB)

    #pics, uuids = wireDB.getTrainingPictures("*")
    #print(pics)
    #print(uuids)
#"""
