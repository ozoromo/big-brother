# @Author: Julius U. Heller <thekalk>
# @Date:   2021-05-19T15:24:34+02:00
# @Project: ODS-Praktikum-Big-Brother
# @Filename: DatabaseManagement.py
# @Last modified by:   Julius U. Heller
# @Last modified time: 2021-06-20T14:49:36+02:00



import numpy as np
import psycopg2 as psy
import pickle
import uuid
#import matplotlib as mpl
import time
import traceback
import cv2
import datetime as dt
from pytz import timezone
import pytz

# Big Brother Database Mangement Class
# Authors: Julius
#
# Manages Database Requests
# can Import and Export Pictures from Database
#
#Server Adress : h2938366.stratoserver.net
#
#
class BBDB:
    #
    # Database Baseclass
    # Subclasses like wire_DB inherit methods and Varaibles
    # This is done to reduce Code and to Unify the usage of the Database
    #

    def __init__(self, dbhost : str, username : str, password : str):

        #
        # Build connection to database
        # # WARNING: Throws error if connection failed!
        #

        self.DBCon = None
        self.username = username
        self.password = password

        self.DBCon = psy.connect(dbname='bigbrother', user=username, password=password,host=dbhost,port="5432",sslmode='require')

        self.DBCon.set_session(autocommit=True)
        self.DBCursor = self.DBCon.cursor()

    def close(self):
        self.DBCon.close()

    def commit(self):

        self.DBCon.commit()

    def delUser(self,**kwargs):

        user_uuid = None
        username = None
        query = ""

        for key, value in kwargs.items():

            if key == 'user_uuid':
                user_uuid = value

            elif key == 'username':
                username = value

        if not username and user_uuid:
            username = self.getUserWithId(user_uuid)
            query = """
            DELETE FROM shared.user_table WHERE user_uuid = '{}';
            """.format(user_uuid)
            self.DBCursor.execute(query)
            return True

        elif username and not user_uuid:
            user_uuid = self.getUser(user_uuid)
            query = """
            DELETE FROM shared.user_table WHERE username = '{}';
            """.format(username)
            print(query)
            self.DBCursor.execute(query)
            return True

        else:
            print("WARNING: Database Login Failed!")
            return False





    def addAdminRelation(self,admin_uuid, child_uuid):
        query = """ INSERT INTO shared.admin_table VALUES ('{}','{}'); """.format(admin_uuid,child_uuid)
        self.DBCursor.execute(query)




    def get_username(self,uuids : list):

        #
        # Fetches Usernames from Database beloging to the given uuids
        #

        ret = []
        #
        # Generate Query with given uuids
        #
        query = """ SELECT username FROM shared.user_table WHERE user_uuid IN {}""".format(tuple(uuids))
        query = query[0:len(query) - 2] + ");"

        self.DBCursor.execute(query)

        ret = self.DBCursor.fetchall()

        usernames = []

        for user in ret:

            usernames.append(user[0])

        #
        # Return List of usernames
        #

        return usernames

    def login_user(self, **kwargs):

        user_uuid = None
        username = None

        for key, value in kwargs.items():

            if key == 'user_uuid':
                user_uuid = value

            elif key == 'username':
                username = value

        if not username and user_uuid:
            username = self.getUserWithId(user_uuid)

        elif username and not user_uuid:
            user_uuid = self.getUser(user_uuid)

        else:
            print("WARNING: Database Login Failed!")
            return False,False



        localTime = dt.datetime.now(tz=timezone('Europe/Amsterdam'))

        query = """
        INSERT INTO shared.login_table VALUES ('{}','{}',false,NULL,false)
        """.format(user_uuid,localTime)

        self.DBCursor.execute(query)

        return localTime

    def update_login(self, **kwargs):

        user_uuid = None
        username = None
        time = None
        inserted_pic_uuid = None

        for key, value in kwargs.items():

            if key == 'user_uuid':
                user_uuid = value

            elif key == 'username':
                username = value

            elif key == 'time':
                time = value

            elif key == 'inserted_pic_uuid':
                inserted_pic_uuid = value

        if not username and user_uuid:
            username = self.getUserWithId(user_uuid)

        elif username and not user_uuid:
            user_uuid = self.getUser(user_uuid)

        else:
            print("WARNING: Database Login Failed!")
            return False,False

        if not time or not inserted_pic_uuid:
            print("WARNING: Database Login Failed!")
            return False,False


        query = """
        UPDATE shared.login_table
        SET login_success = true, inserted_pic_uuid = '{}'
        WHERE user_uuid = '{}' AND login_date = '{}';
        """.format(inserted_pic_uuid,user_uuid,time)

        self.DBCursor.execute(query)

        return True




    def register_user(self,username : str):

        #
        # Register a user in the shared Database
        # makes sure that the new uuid is unique
        # Returns:
        # True on Succes
        #
        # Raises:
        # UsernameExists Exception
        #

        #Fetch Users and their uuids

        users = self.getUsers()
        new_uuid = uuid.uuid1()

        for existing_uuid in users:
            while existing_uuid == new_uuid:
                # If the new uuid is not unique make a new one
                new_uuid = uuid.uuid1()


        #
        # Generate query
        #

        query = """
        INSERT INTO shared.user_table (USER_UUID,USERNAME) VALUES('{}','{}');

        """.format(new_uuid,username)

        #
        # If the username is not unique UsernameExists error is thrown
        #

        try:

            self.DBCursor.execute(query)

        except (psy.errors.UniqueViolation):

            raise UsernameExists("Username in use!")


        return new_uuid

    def getUsers(self,limit = -1):

        #
        # Fetches all Users with their uuid
        # Output:
        #   Dictionary
        #       key : uuid
        #       value : username
        #
        query = ""
        if limit < 0:
            query = """
            SELECT * FROM shared.user_table ORDER BY username;
            """
        else:
            query = """
            SELECT * FROM shared.user_table ORDER BY username LIMIT {};
            """.format(limit)

        self.DBCursor.execute(query)

        user_dict = {}

        for users in self.DBCursor.fetchall():

            user_dict[users[0]] = users[1]

        return user_dict

    def getUserWithId(self,u_uuid):

        #
        # Fetches a specific uuid1
        # Returns: uuid of given user
        #

        query = """
        SELECT username FROM shared.user_table WHERE user_uuid = '{}';
        """.format(u_uuid)
        self.DBCursor.execute(query)

        ret = self.DBCursor.fetchall()

        if len(ret) == 0:

            return None

        username = ret[0]
        if type(username) == tuple:
            username = username[0]


        return username

    def deleteUserWithId(self,u_uuid):

        #
        # Deltes User with specific uuid
        # Returns: True
        #

        query = """
        DELETE FROM shared.user_table WHERE user_uuid = '{}';
        """.format(u_uuid)
        self.DBCursor.execute(query)

        return True

    def getUser(self,username):

        #
        # Fetches a specific uuid1
        # Returns: uuid of given user
        #

        query = """
        SELECT user_uuid FROM shared.user_table WHERE username = '{}';
        """.format(username)
        self.DBCursor.execute(query)

        ret = self.DBCursor.fetchall()

        if len(ret) == 0:

            return None

        if type(ret[0]) == tuple:
            return ret[0][0]

        return ret[0]


    def insertPicture(self, pic : np.ndarray, user_uuid : uuid.UUID):

        # Returns True/False on Success or Error
        # Pickles Picture and inserts it into DB
        # pic : picture to be saved as np.ndarray
        # user_uuid : id of user wich owns picture

        #
        ## TODO: Error Handling, in the rare case that a duplicate uuid is generated this method has to try again
        #

        return False

    def getPicture(self,query : str):
        return False

    def closeGraceful(self):

        #
        # Should be called everytime the Program Shuts down so that the Server
        # Doesnt overflow with psql processes
        # This includes all Exceptions
        #

        self.DBCon.close()

class wire_DB(BBDB):
    #
    # Subclass from BBDB
    # Inherits Methods and Variables
    #

    def __init__(self, dbhost : str):

        #
        # Call Superclass init
        #

        BBDB.__init__(self, dbhost, 'backend', 'NfPNlXBcYtIATJIGcuIR')

    def insertTrainingPicture(self, pic : np.ndarray, user_uuid : uuid.UUID):

        # Inserts a Training Picture into the Database
        # Returns picture uuid
        # Pickles Picture and inserts it into DB
        # pic : picture to be saved as np.ndarray
        # user_uuid : id of user wich owns picture

        #
        ## TODO: Error Handling, in the rare case that a duplicate uuid is generated this method has to try again
        #

        #
        # Format Checking
        #

        if type(pic) != np.ndarray:
            return False

        if type(user_uuid) != uuid.UUID:
            return False

        #
        # Generate a uuid for the picture
        #

        pic_uuid = str(uuid.uuid1())

        #
        # Dumps the ndarray into a bytearray and sends the Query to the DB
        #

        self.DBCursor.execute(
            """
            INSERT INTO backend.wire_train_pictures(pic_uuid, user_uuid, pic_data)
            VALUES (%s, %s, %s);
            """,(pic_uuid,str(user_uuid), pickle.dumps(pic))
            )

        #
        # Success
        #

        return pic_uuid

    def getTrainingPictures(self, where : str):
        #
        # Gets training Pictures for wire
        # USAGE:
        # columns must be in SQL format: 'column1,column2'
        # or : '*'
        # WHERE statement must be in SQL format: """WHERE 'name' = 'John Doe' """
        # or : '*'

        #query = """
        #SELECT {} FROM wire_train_pictures {};
        #""".format(columns,where)
        query = """
        SELECT pic_uuid,pic_data FROM wire_train_pictures {};
        """.format(where)

        self.DBCursor.execute(query)

        ret = self.DBCursor.fetchall()

        pics = []
        uuids = []

        for row in ret:

            #
            # Order Fetched Data and 'undump'
            #

            pics.append(pickle.loads(row[1]))
            uuids.append(row[0])

        return pics,uuids

    def getAllTrainingsImages (self):

        query = """
        SELECT pic_uuid, pic_data, user_uuid FROM wire_train_pictures;
        """

        self.DBCursor.execute(query)

        ret = self.DBCursor.fetchall()

        pics = []
        uuids = []
        user_uuids = []

        for row in ret:

            #
            # Order Fetched Data and 'undump'
            #

            pics.append(pickle.loads(row[1]))
            uuids.append(row[0])
            user_uuids.append(row[2])

        return pics,uuids,user_uuids



class opencv_DB(BBDB):

    def __init__(self, dbhost : str):

        #
        # Call Superclass init
        #

        BBDB.__init__(self, dbhost, 'backend', 'NfPNlXBcYtIATJIGcuIR')

    #
    # # TODO: Ich muss vom Opencv team jetzt wissen was für Tables ihr braucht
    # Damit ich die Datenbank funktionen für euch schreiben kann
    #






class frontend_DB(BBDB):
    def __init__(self, dbhost : str):

        BBDB.__init__(self, dbhost, 'frontend', 'K6i0aI6cbV2inmuyK4SN')


class UsernameExists(Exception):
    pass

def makeSuperAdmin(name):

    this = wire_DB("h2938366.stratoserver.net")

    admin_uuid = this.getUser(name)

    user_dict = this.getUsers()

    childCount = 20

    addedChilds = []

    for child in range(childCount):

        user_uuid, username = random.choice(list(user_dict.items()))

        while user_uuid in addedChilds:
            user_uuid, username = random.choice(list(user_dict.items()))

        addedChilds.append(user_uuid)



        try:

            this.addAdminRelation(admin_uuid,user_uuid)
            print("added: {} -> {}".format(admin_uuid,user_uuid))

        except psy.errors.UniqueViolation:
            print("Encountered UniqueViolation")
            pass

def delThisUser(name):
    this = wire_DB("h2938366.stratoserver.net")
    print(this.delUser(username=name))
    this.commit()



if __name__ == '__main__':
    import random
    #delThisUser("julius_falseTest")
    makeSuperAdmin("julius1")
