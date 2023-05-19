# @Author: Julian Flieller <@Dr.Hype#0001>
# @Date:   2023-05-13
# @Project: ODS-Praktikum-Big-Brother
# @Filename: new_database_management.py
# @Last modified by:   Julian FLieller
# @Last modified time: 2023-05-19

"""Big Brother Database Mangement Class

Manages Database Requests
can Import and Export Pictures from Database
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
    #I kinda dont get why as it only creates more overhead, since it only creates a new instance of BDBB

    # we COULD simplify/remove a lot of the functions to have less overhead and make it more readable,
    # but we´d have to adjust the methods in the other files as well
    def __init__(self,dbhost:str=None,username:str=None,password:str=None):
        #remove arguments, they are not needed anymore
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
        #REMOVEABLE
        """
        not needed for mongodb
        """
        return

    def delUser(self,**kwargs)-> bool:
        """
        Delete a user from the database with the given uuid or username
        """
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

    def addAdminRelation(self,admin_uuid,child_uuid): 
        #maybe simplify arguments as the old ones are confusing
        #as far as I can tell from the diagram, the child_uuid is the user_uuid
        """
        Add a user as an admin with the given child_uuid aka user_uuid
        """
        if self.user_table.find_one({"user_uuid":child_uuid}): #added a check if the user exists
            self.user_table.update_one({"user_uuid":child_uuid},{"$set":{"is_admin":True}})

    def get_username(self,uuids:list):
        '''
        Fetches usernames from database belonging to the given uuids
        '''
        usernames = []
        for uuid in uuids:
            usernames.append(self.user_table.find_one({"user_uuid":uuid})["username"])
        return usernames

    def login_user(self, **kwargs):
        '''
        Creates a new entry in the login_table for the user with the given uuid or username
        '''
        username, user_uuid = None, None
        for key, value in kwargs.items():
            if key == 'user_uuid':
                user_uuid = value

            elif key == 'username':
                username = value

        #removed getUserWithId() & getUser() call here, as I find the function unnecessary for only 2 calls + the naming is weird as it only returns the username and not the whole user
        if user_uuid and not username:
            username = self.user_table.find_one({"user_uuid":user_uuid})["username"] 
        elif username and not user_uuid:
            user_uuid = self.user_table.find_one({"username":username})["user_uuid"]
        else:
            print("WARNING: Database Login Failed!")
            return False,False #TODO: why return False twice?
        
        localTime = dt.datetime.now(tz=timezone('Europe/Amsterdam'))
        self.login_table.insert_one({"user_uuid":user_uuid,"username":username,"date":localTime,"login":False,"inserted_pic":None})

        return localTime
        
    def update_login(self, **kwargs):
        user_uuid,username,item,inserted_pic_uuid = None,None,None,None
        
        for key, value in kwargs.items():
            if key == 'user_uuid':
                user_uuid = value
            elif key == 'username':
                username = value
            elif key == 'time':
                time = value
            elif key == 'inserted_pic_uuid':
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
        
        self.login_table.update_one({"user_uuid":user_uuid,"username":username,"date":time},{"$set":{"login_success":True,"inserted_pic":inserted_pic_uuid}})
        return True

    def register_user(self,username:str):
        '''
        Creates a new user in the database with the given username
        '''
        users = self.getUsers()
        new_uuid = uuid.uuid1()

        #makes sure that the new uuid is unique
        for existing_uuid in users:
            while existing_uuid == new_uuid:
                new_uuid = uuid.uuid1()

        if self.user_table.find_one({"username":username}):
            raise UsernameExists("Username in use!")
        else:
            self.user_table.insert_one({"username":username,"user_uuid":new_uuid,"is_admin":False})
            return new_uuid

    def getUsers(self,limit = -1):
        '''
        Fetches all Users with their uuids and usernames from the database
        '''
        user_dict = {}
        if limit < 0:
            for user in self.user_table.find():
                user_dict.append({
                    "key": user["user_uuid"],
                    "value": user["username"]
                })
        else:
            for user in self.user_table.find().limit(limit):
                user_dict.append({
                    "key": user["user_uuid"],
                    "value": user["username"]
                })
        return user_dict
            
    def getUserWithId(self,u_uuid): 
        #REMOVEABLE + why u_uuid and not user_uuid?
        self.user_table.find_one({"user_uuid":u_uuid})["username"] 

    def deleteUserWithId(self,u_uuid):
        '''
        Deletes the user with the given uuid from the database
        '''
        #added error handling if the user does not exist
        if self.user_table.find_one({"user_uuid":u_uuid}):
            self.user_table.delete_one({"user_uuid":u_uuid})
            return True
        else:
            return False

    def getUser(self,username):
        self.user_table.find_one({"username":username})["user_uuid"]

    def insertPicture(self, pic : np.ndarray, user_uuid : uuid.UUID):
        #was not implemented yet
        raise NotImplementedError

    def getPicture(self,query : str):
        #was not implemented yet
        raise NotImplementedError

    def closeGraceful(self):
        #REMOVEABLE
        self.close()
        raise NotImplementedError

class wire_DB(BBDB):
    """Subclass from BBDB
    Inherits Methods and Variables"""

    def __init__(self,dbhost:str=None):
        BBDB.__init__(self)

    #Move those functions to the BBDB class
    def insertTrainingPicture(self,pic:np.ndarray,user_uuid:uuid.UUID):
        '''
        Inserts a new training picture into the database and returns the uuid of the inserted picture
        '''
        if type(pic) != np.ndarray or type(user_uuid) != uuid.UUID:
            return False
        
        pic_uuid = str(uuid.uuid1())
        self.wire_train_pictures.insert_one({"user_uuid":user_uuid,"pic_data":pic,"pic_uuid":pic_uuid})
        return pic_uuid

    def getTrainingPictures(self, where : str):
        #not sure how ti implement the where clause, I think we should change the logic here
        raise NotImplementedError

    def getAllTrainingsImages(self):
        '''
        Returns all training images from the database in three lists: pics, uuids, user_uuids
        '''
        pics,uuids,user_uuids=[],[],[]
        for pic in self.wire_train_pictures.find():
            pics.append(pickle.loads(pic["pic_data"]))
            uuids.append(pic["pic_uuid"])
            user_uuids.append(pic["user_uuid"])
        return pics,uuids,user_uuids



class opencv_DB(BBDB):
    #REMOVEABLE
    def __init__(self,dbhost:str=None):
        BBDB.__init__(self)


class frontend_DB(BBDB):
    #REMOVEABLE
    def __init__(self,dbhost:str=None):
        BBDB.__init__(self)


class UsernameExists(Exception):
    #????? NOTHING DONE HERE; REMOVEABLE FS
    pass

def makeSuperAdmin(name):
    #REMOVEABLE, not being used
    raise NotImplementedError

def delThisUser(name):
    #REMOVEABLE, not being used
    raise NotImplementedError

'''
#only for testing, remove in production
if __name__ == '__main__':
    DB = BBDB()
'''  
