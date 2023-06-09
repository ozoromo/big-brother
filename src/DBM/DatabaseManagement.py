"""Big Brother Database Mangement Class

Manages Database Requests
can Import and Export Pictures from Database

@Author: Julian Flieller <@Dr.Hype#0001>
@Date:   2023-05-13
@Project: ODS-Praktikum-Big-Brother
@Filename: new_database_management.py
@Last modified by:   Julian Flieller
@Last modified time: 2023-05-31
"""
import numpy as np
import pickle
import uuid
import datetime as dt
from pytz import timezone
from gridfs import GridFS
import pymongo


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

        db = self.cluster["BigBrother"]
<<<<<<< HEAD
        self.train_videos = db["train_videos"]
        self.wire_train_pictures = db["wire_train_pictures"]
        self.user_table = db["user_table"]
        self.admin_table = db["admin_table"]
        self.login_table = db["login_table"]
        self.benchmark_pictures = db["benchmark_pictures"]
        self.gesture_videos = db["gesture_videos"]
=======
        self.user = db["user"]
        self.login_attempt = db["login_attempt"]
        self.resource = db["resource"]
        self.resource_context = db["resource_context"]
>>>>>>> DB/tests

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
        if self.user.find_one({"_id": user_id}):
            self.user.delete_one({"_id": user_id})
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
        if self.user.find_one({"_id": user_id}):
            self.user.update_one({"_id": user_id}, {"$set": {"is_admin": True}})
            return True
        print("WARNING: AddAdminRelation Failed!")
        return False

    def getUsername(self, uuids: list):
        """
        Fetches usernames from database belonging to the given uuids

        Arguments:
        uuids -- This is a list of user_uuid. Those are the uuids of which you want to get the usernames.

        Return:
        Returns the a list of usernames that correspond to the user_uuid
        that have been inputted. The index i of the return list corresponds
        to uuids[i] in the input.
        """
        usernames = []
        for user_id in uuids:
            usernames.append(self.user.find_one({"_id": str(user_id)})["username"])
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
        if self.user.find_one({"_id":user_id}):
            self.login_attempt.insert_one({
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
            self.login_attempt.update_one(
                {
                    "user_id": user_id,
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

    def register_user(self, username: str, user_enc_res_id: uuid.UUID):
        """
        Creates a new user in the database with the given username.

        Arguments:
        username -- The username of the new user.
        user_enc_res_id -- user_enc_res_id of the user (identifier from opencv)

        Return:
        If the user has been successfully registered then it returns the
        user_id of the user what has been created.

        Exception:
        Raises an exception if the username already exists.
        """
        new_uuid = uuid.uuid1()
        for existing_uuid in self.getUsers():
            while existing_uuid == new_uuid:
                new_uuid = uuid.uuid1()

        if self.user.find_one({"username" : username}):
            raise UsernameExists("Username in use!")
        else:
            self.user.insert_one({
                "_id": str(new_uuid),
                "username" : username, 
                "user_enc_res_id" : str(user_enc_res_id),
                "is_admin" : False})
            return new_uuid

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
        users = self.user.find()
        if limit == 0:
            return {}
        elif limit > 0:
            users = users.limit(limit)

        user_dict = {}
        for user in users:
            user_dict[uuid.UUID(user["_id"])] = user["username"]
        return user_dict
            
    def getUserWithId(self, user_id: uuid.UUID) -> str:
        """
        Returns the username corresponding to the user_id.

        Arguments:
        user_id -- The user_id aka _id.

        Return:  
        Returns the username corresponding to the user_id. If the user with the
        given ID doesn't exist then None gets returned.
        """
        user_entry = self.user.find_one({"_id" : str(user_id)})
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
        if self.user.find_one({"_id": user_id}):
            self.delUser(user_id)
            self.login_attempt.delete_many({"user_id": user_id}) 
            self.resource.delete_many({"user_id": user_id})
            # TODO: resource_context also needs to get updated
            return True
        return False

    def getUser(self, username: str) -> uuid.UUID:
        """
        Returns the uuid corresponding to the username.

        Arguments:
        username -- The username of the user.

        Return:
        Returns the uuid corresponding to the username. If the username
        doesn't exist then it returns None.
        """
        user_entry = self.user.find_one({"username": username})
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
        if not self.resource_context.find({"name": "wire"}):
            self.resource_context.insert_one({
                "_id": uuid.uuid1(), # TODO: Collision is possible. If many items in resource_context
                                     # get generated at the same time (e.g. by multiple clients). 
                                     # Also if other items in resource_context get generated.
                "name": "wire",
                "username": None,
                "res_id": []})
        self.wire_context_collection = self.resource_context.find({"name": "wire"})

    def getTrainingPictures(self, user_uuid: uuid.UUID = None):
        """
        Returns training pictures from the database from the wire resource context
        """

        # TODO: We need to be able to verify whether a certain user with the 
        # user_id exists before we check
        # TODO: Find a way to make this prettier
        resources = None
        if user_uuid: 
            resources = self.resource.find({
                        "_id": {"$in": self.wire_context_collection["res_id"]},
                        "user_id": str(user_uuid),
                    })
        else: 
            resources = self.resource.find({
                        "_id": {"$in": self.wire_context_collection["res_id"]},
                    })

        return [pickle.loads(r["res"]) for r in resources]
    
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
        
        # TODO: There might be some problems if multiple files are inserted
        # concurrently
        pic_uuid = str(uuid.uuid1())
        self.resource.insert_one({
            "_id" : pic_uuid,
            "user_id": str(user_uuid),
            "res" : pickle.dumps(pic),
            "date": dt.datetime.now(tz=timezone('Europe/Amsterdam')),
            "pic_uuid": pic_uuid
        })
        self.resource_context.update_one(
                {"name": "wire"},
                {"$addToSet": {"res_id": pic_uuid}})
        return uuid.UUID(pic_uuid)


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

    def __init__(self,dbhost:str=None):
        BBDB.__init__(self)

    def insertVideo(self, vid:np.ndarray, user_uuid:uuid.UUID):
        """
        Inserts a new video into the database and returns the 
        uuid of the inserted video.

        Arguments:
        vid       -- Video to be inserted into the database.
        user_uuid -- ID of the user that owns the video.

        Return:
        Returns the uuid of the video that has been inserted into the database.

        Exception:
        TypeError -- Gets risen if the type of the input isn't the expected type.
        """

        if type(vid) != np.ndarray or type(user_uuid) != uuid.UUID:
           raise TypeError
        
        bucket = GridFS(self.train_videos)
        
        # TODO: vid_uuid can be stored in GridFS file with the video
        # vid_uuid = str(uuid.uuid1())
        video_id = bucket.put(pickle.dumps(vid), user_uuid=user_uuid)
        
        return video_id

    def getVideo(self, video_id:str):

        bucket = GridFS(self.train_videos)
        video = pickle.load(bucket.get(video_id))
        # TODO: create video stream functionality
        # video_stream = bucket.openDownloadStream()

        return video




class opencv_DB(BBDB):
    def __init__(self):
        BBDB.__init__(self)


class frontend_DB(BBDB):
    def __init__(self):
        BBDB.__init__(self)


class UsernameExists(Exception):
    pass

"""
# only for testing, remove in production
if __name__ == '__main__':
    DB = BBDB()
    DB.register_user("mike")
    print(list(DB.user_table.find()))
"""
