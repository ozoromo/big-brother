"""Big Brother Database Mangement Class

Manages Database Requests
can Import and Export Pictures from Database

@Author: Julian Flieller <@Dr.Hype#0001>
@Date:   2023-05-13
@Project: ODS-Praktikum-Big-Brother
@Filename: new_database_management.py
@Last modified by:   Julian FLieller
@Last modified time: 2023-05-19
"""
import numpy as np
import pickle
import uuid
import datetime as dt
from pytz import timezone
import pymongo

class BBDB:
    """Database Baseclass
    Subclasses like wire_DB inherit methods and Varaibles
    This is done to reduce Code and to Unify the usage of the Database""" 
    # I kinda dont get why as it only creates more overhead, 
    # since it only creates a new instance of BDBB

    # TODO: we COULD simplify/remove a lot of the functions to have 
    # less overhead and make it more readable,
    # but we´d have to adjust the methods in the other files as well
    def __init__(self,dbhost:str=None,username:str=None,password:str=None):
        # TODO: remove arguments, they are not needed anymore
        """
        Builds up the initial connection to the database
        """
        self.cluster = pymongo.MongoClient("mongodb+srv://admin:7EgqBof7tSUKlYBN@bigbrother.qse5xtp.mongodb.net/?retryWrites=true&w=majority",connectTimeoutMS=30000,socketTimeoutMS=None,connect=False,maxPoolsize=1)
        db = self.cluster["BigBrother"]
        self.wire_train_pictures = db["wire_train_pictures"]
        self.user_table = db["user_table"]
        self.admin_table = db["admin_table"]
        self.login_table = db["login_table"]
        self.benchmark_pictures = db["benchmark_pictures"]
        self.gesture_videos = db["gesture_videos"]

    def close(self):
        """
        Close the connection with the database
        """
        self.cluster.close()

    def commit(self):
        """
        not needed for mongodb
        """
        # TODO: Talk about it. This might be used somewhere in order
        # to "take back" some entries.
        return

    def delUser(self,**kwargs)-> bool:
        """
        Delete a user from the database with the given uuid or username

        Keyword arguments: Only one of the keyword arguments should 
        be set. Otherwise an error will be returned.  
        user_uuid -- ID of the user that you want to delete.  
        username  -- Username of the user that you want to delete.
        """
        # TODO: Discuss. Only use one unique identifier internally. 
        # Of course the username still has to be unique, but the API
        # should only support one of them being used for operations.
        for key, value in kwargs.items():
            if key == "user_uuid":
                user_uuid = value
            elif key == "username":
                username = value

        if user_uuid and not username:
            self.user_table.delete_one({"user_uuid":user_uuid})
            return True 
        elif username and not user_uuid:
            self.user_table.delete_one({"username":username})
            return True
        else:
            print("WARNING: Database Login Failed!")
            return False

    def addAdminRelation(self, admin_uuid, child_uuid): 
        """
        Add a user as an admin with the given child_uuid aka user_uuid

        Arguments:
        admin_uuid -- This variable is depricated and isn't really used.  
        child_uuid -- This is the user_id of the user that should be made admin.
        """
        # TODO: maybe simplify arguments as the old ones are confusing
        # as far as I can tell from the diagram, the child_uuid is the user_uuid
        # TODO: Discuss. Perhaps return whether it worked or not (like in @{code delUser()}).
        if self.user_table.find_one({"user_uuid":child_uuid}): #added a check if the user exists
            self.user_table.update_one({"user_uuid":child_uuid},{"$set":{"is_admin":True}})

    def get_username(self,uuids:list):
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
        for uuid in uuids:
            usernames.append(self.user_table.find_one({"user_uuid":uuid})["username"])
        return usernames

    def login_user(self, **kwargs):
        """
        Creates a new entry in the login_table for the user with the given uuid or username.

        Keyword arguments: Only one of the keyword arguments should be set. Otherwise an error will be returned.  
        user_uuid -- ID of the user that you want to delete.
        username  -- Username of the user that you want to delete.

        Return:  
        Returns (False,False) if the login fails and the timestamp of the
        login if it succeeds.
        """
        # TODO: Only use one identifier in order for the API.
        username, user_uuid = None, None
        for key, value in kwargs.items():
            if key == 'user_uuid':
                user_uuid = value
            elif key == 'username':
                username = value

        if user_uuid and not username:
            username = self.user_table.find_one({"user_uuid":user_uuid})["username"] 
        elif username and not user_uuid:
            user_uuid = self.user_table.find_one({"username":username})["user_uuid"]
        else:
            print("WARNING: Database Login Failed!")
            return False,False # TODO: why return False twice?
        
        localTime = dt.datetime.now(tz=timezone('Europe/Amsterdam'))
        self.login_table.insert_one({
            "user_uuid" : user_uuid,
            "username" : username,
            "date" : localTime,
            "login" : False,
            "inserted_pic" : None
            })

        return localTime
        
    def update_login(self, **kwargs):
        """
        Updates the status of the login of one user with a certain 
        user_uuid or username.

        Keyword arguments:
        user_id -- ID of the user of which you want to log in. You can only set 
        either the user_id or the username otherwise you are going to get an error.
        username -- Username of the user which you want to log in. You can only
        set either the user_id or the username otherwise you are going to get an error.
        time -- The timestamp of the login you want to update. 
        """
        # TODO: Why can you only pass either user_id or username?
        # TODO: Only use one identifier. For the API.
        user_uuid = username = time = inserted_pic_uuid = None
        
        for key, value in kwargs.items():
            if key == "user_uuid":
                user_uuid = value
            elif key == "username":
                username = value
            elif key == "time":
                time = value
            elif key == "inserted_pic_uuid":
                inserted_pic_uuid = value
        
        if user_uuid and not username:
            username = self.user_table.find_one({"user_uuid":user_uuid})["username"] 
        elif username and not user_uuid:
            user_uuid = self.user_table.find_one({"username":username})["user_uuid"]
        else:
            print("WARNING: Database Login Failed!")
            return False,False #TODO: why return False twice?

        if not time or not inserted_pic_uuid:
            print("WARNING: Database Login Failed!")
            return False,False
        
        self.login_table.update_one(
            {
                "user_uuid" : user_uuid,
                "username"  : username, 
                "date"      : time
            },
            { "$set" : {
                "login_success" : True,
                "inserted_pic" : inserted_pic_uuid
                }
             })
        return True

    def register_user(self,username:str):
        """
        Creates a new user in the database with the given username.

        Arguments:  
        username -- The username of the new user.

        Return:  
        If the user has been successfully registered then it returns the
        user_uuid of the user what has been created.

        Exception:  
        Raises an exception if the username already exists.
        """
        # TODO: maybe change type?
        users = self.getUsers()
        new_uuid = str(uuid.uuid1())

        # makes sure that the new uuid is unique
        for existing_uuid in users:
            while existing_uuid == new_uuid:
                new_uuid = str(uuid.uuid1())

        if self.user_table.find_one({"username" : username}):
            raise UsernameExists("Username in use!")
        else:
            self.user_table.insert_one({
                "username" : username, 
                "user_uuid" : new_uuid,
                "is_admin" : False})
            return new_uuid

    def getUsers(self,limit = -1):
        """
        Fetches all Users with their uuids and usernames from the database

        Optional arguments:  
        limit -- This argument sets the amount of users that you want to limit 
        your request to. If it's set to a negative number (which it is by default),
        then the search isn't limited.

        Return:  
        If `limit` is negative then it returns a dictionary of all users and the 
        associated usernames. If the limit is non-negative then it returns a
        list wiht `limit` amount of entries. The dictionary key are the user_uuid
        and the value is the username.
        """
        users = self.user_table.find()
        if limit >= 0:
            users = users.limit(limit)

        user_dict = {}
        for user in users:
            user_dict[user["user_uuid"]] = user["username"]
        return user_dict
            
    def getUserWithId(self, user_uuid): 
        """
        Returns the username corresponding to the user_uuid.

        Arguments:
        user_uuid -- The user_uuid.

        Return:  
        Returns the username corresponding to the user_uuid. If the user with the
        given ID doesn't exist then None gets returned.
        """
        # TODO: REMOVEABLE
        # TODO: It might make the code cleaner to leave it there.
        user_entry = self.user_table.find_one({"user_uuid" : user_uuid})
        if user_entry is None: 
            return None
        return user_entry["username"]

    def deleteUserWithId(self,user_uuid):
        """
        Deletes the user with the given user_uuid from the database.

        Arguments:
        user_uuid: ID of the user that should be deleted.

        Return:
        Returns True if the user has been successfully deleted. And 
        False otherwise (e.g. user didn't exist in the database).
        """
        # TODO: What happens with the entries that refer to the user
        # with the user_uuid tha have been deleted. They should also 
        # be deleted. Otherwise there some inconsistencies might arise.

        # added error handling if the user does not exist
        if self.user_table.find_one({"user_uuid" : user_uuid}):
            self.user_table.delete_one({"user_uuid" : user_uuid})
            return True
        else:
            return False

    def getUser(self, username):
        """
        Returns the uuid corresponding to the username.

        Arguments:  
        username -- The username of the user.

        Return:  
        Returns the uuid corresponding to the username. If the username 
        doesn't exist then it returns None.
        """
        user_entry = self.user_table.find_one({"username" : username})
        if user_entry is None: 
            return None
        return user_entry["user_uuid"]

    def insertPicture(self, pic : np.ndarray, user_uuid : uuid.UUID):
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
        # TODO: was not implemented yet
        raise NotImplementedError

    def closeGraceful(self):
        """
        Should be called everytime the Program Shuts down so that the Server
        Doesnt overflow with psql processes
        This includes all Exceptions
        """
        # TODO: remove
        # TODO: Take a look at the use-case of this function. How should it
        # differ from the close-function
        self.close()

class wire_DB(BBDB):
    """Subclass from BBDB
    Inherits Methods and Variables"""

    def __init__(self,dbhost:str=None):
        BBDB.__init__(self)

    # TODO: Move those functions to the BBDB class
    def insertTrainingPicture(self, pic:np.ndarray, user_uuid:uuid.UUID):
        """
        Inserts a new training picture into the database and returns the 
        uuid of the inserted picture.

        Arguments:  
        pic       -- Picture to be inserted into the database.
        user_uuid -- ID of the user which owns the picture.

        Return:  
        Returns the uuid of the picture that has been inserted into the database.

        Exception:
        TypeError -- Gets risen if the type of the input isn't the expected type.
        """
        # TODO: Only commented out for testing purposes
        #if type(pic) != np.ndarray or type(user_uuid) != uuid.UUID:
        #    raise TypeError
        
        # TODO: Make sure pic_uuid is unique?
        pic_uuid = str(uuid.uuid1())
        self.wire_train_pictures.insert_one({
            "user_uuid" : user_uuid,
            "pic_data" : pickle.dumps(pic),
            "pic_uuid" : pic_uuid})
        return pic_uuid

    def getTrainingPictures(self, where : str):
        """
        Returns training pictures from the database with the given where clause
        """
        # TODO: Discuss. Change the logic of this function, because the 
        # is hard to parse.
        # TODO: This code is likely not to be correct. Change this code!
        pics,uuids = [],[]
        where = where.replace(" ","") #removes all whitespaces to have a cleaner format to work with
        if "where" == "*":
            for pic in self.wire_train_pictures.find():
                pics.append(pickle.loads(pic["pic_data"]))
                uuids.append(pic["pic_uuid"])
        else:
            pass
            #assuming that where is always of the format """WHERE 'name' = 'John Doe' """
            #self.wire_train_pictures.find({"name":where.split("='")[1].split("'")[0]})
            #pics.append(pickle.loads(pic["pic_data"]))
            #uuids.append(pic["pic_uuid"])
        
        return pics,uuids

    def getAllTrainingsImages(self):
        """
        Returns all training images from the database in three lists: 
        pics, uuids, user_uuids
        """
        pics,uuids,user_uuids=[],[],[]
        for pic in self.wire_train_pictures.find():
            pics.append(pickle.loads(pic["pic_data"]))
            uuids.append(pic["pic_uuid"])
            user_uuids.append(pic["user_uuid"])
        return pics, uuids, user_uuids

class opencv_DB(BBDB):
    # TODO: Discuss. REMOVEABLE?
    def __init__(self,dbhost:str=None):
        BBDB.__init__(self)


class frontend_DB(BBDB):
    # TODO: Discuss. REMOVEABLE?
    def __init__(self,dbhost:str=None):
        BBDB.__init__(self)


class UsernameExists(Exception):
    pass

def makeSuperAdmin(name):
    # TODO: Discuss. Remove.
    raise NotImplementedError

def delThisUser(name):
    # TODO: Discuss. Remove.
    raise NotImplementedError

"""
# TODO: only for testing, remove in production
if __name__ == '__main__':
    DB = BBDB()
    DB.register_user("mike")
    print(list(DB.user_table.find()))
"""
