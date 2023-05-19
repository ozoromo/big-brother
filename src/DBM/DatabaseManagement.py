"""Big Brother Database Mangement Class

Manages Database Requests
can Import and Export Pictures from Database
"""
import pymongo
import numpy as np
import uuid


class BBDB:
    """Database Baseclass
    Subclasses like wire_DB inherit methods and Varaibles
    This is done to reduce Code and to Unify the usage of the Database"""

    def __init__(self, dbhost : str, username : str, password : str):
        """
        Builds up the initial connection to the database.

        Argumants:
        dbhost -- **TODO** Remove this, because it's no longer used
        username -- Database username.
        password -- Password associated to the user.
        """
        # TODO: Remove db parameter and change other dependencies to reflect this.
        
        # TODO: Remove this when you finish testing
        username = "mike"
        password = "ThisPasswordMightNotBeSafe."

        dbhost=f"mongodb+srv://{username}:{password}@test.4m57ch3.mongodb.net/?retryWrites=true&w=majority"
        cluster = pymongo.MongoClient(dbhost)
        self.db = cluster["BigBrother"]
        
        # TODO: Remove this
        user_collection = self.db["user"]
        user_collection.insert_one({"username": "Bob", "is_admin": False})

    def close(self):
        """
        Close the connection with the database.
        """
        # TODO: Implement it
        raise NotImplementedError

    def commit(self):
        """
        Commit the changes to the database.
        """
        # TODO: Implement it
        raise NotImplementedError

    def delUser(self,**kwargs):
        """
        Delete a user from the database.
        """
        # TODO: Implement it
        raise NotImplementedError

    def addAdminRelation(self,admin_uuid, child_uuid):
        """
        Add a user as an admin.
        """
        # TODO: Implement it
        raise NotImplementedError

    def get_username(self,uuids : list):
        raise NotImplementedError

    def login_user(self, **kwargs):
        raise NotImplementedError

    def update_login(self, **kwargs):
        raise NotImplementedError

    def register_user(self,username : str):
        raise NotImplementedError

    def getUsers(self,limit = -1):
        raise NotImplementedError

    def getUserWithId(self,u_uuid):
        raise NotImplementedError

    def deleteUserWithId(self,u_uuid):
        raise NotImplementedError

    def getUser(self,username):
        raise NotImplementedError

    def insertPicture(self, pic : np.ndarray, user_uuid : uuid.UUID):
        raise NotImplementedError

    def getPicture(self,query : str):
        raise NotImplementedError

    def closeGraceful(self):
        raise NotImplementedError

class wire_DB(BBDB):
    """Subclass from BBDB
    Inherits Methods and Variables"""

    def __init__(self, dbhost : str):
        raise NotImplementedError

    def insertTrainingPicture(self, pic : np.ndarray, user_uuid : uuid.UUID):
        raise NotImplementedError

    def getTrainingPictures(self, where : str):
        raise NotImplementedError

    def getAllTrainingsImages (self):
        raise NotImplementedError


class opencv_DB(BBDB):

    def __init__(self, dbhost : str):
        raise NotImplementedError


class frontend_DB(BBDB):
    def __init__(self, dbhost : str):
        raise NotImplementedError


class UsernameExists(Exception):
    pass

def makeSuperAdmin(name):
    raise NotImplementedError

def delThisUser(name):
    raise NotImplementedError

if __name__ == '__main__':
    DB = BBDB("doesn't matter","doesn't matter","doesn't matter")
    
