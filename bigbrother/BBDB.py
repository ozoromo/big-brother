import numpy as np
import psycopg2 as psy
import pickle
import uuid
import matplotlib.pyplot as plt
import matplotlib as mpl
import time
import traceback

# Big Brother Database Mangement Class
# Authors: Julius
#
# Manages Database Requests
# can Import and Export Pictures from Database
#
#Server Adress :
#
#
class BBDB:

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

    def getUsers(self):
        query = """
        SELECT * FROM shared.user_table;
        """
        self.DBCursor.execute(query)

        user_dict = {}

        for users in self.DBCursor.fetchall():

            user_dict[users[0]] = users[1]

        return user_dict


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

    def __init__(self, dbhost : str):

        BBDB.__init__(self, dbhost, 'backend', 'NfPNlXBcYtIATJIGcuIR')

    def insertTrainingPicture(self, pic : np.ndarray, user_uuid : uuid.UUID):

        # Returns True/False on Success or Error
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

        pic_uuid = str(uuid.uuid4())

        #
        # Dumps the ndarray into a bytearray and sends the Query to the DB
        #

        self.DBCursor.execute(
            """
            INSERT INTO {}(pic_uuid, user_uuid, pic_data)
            VALUES ({}, {}, {});
            """.format('wire_train',pic_uuid,str(user_uuid), pickle.dumps(pic))
            )

        #
        # Success
        #

        return True

    def getTrainingPictures(columns : str, where : str):
        #
        # Gets training Pictures for wire
        # USAGE:
        # columns must be in SQL format: 'column1,column2'
        # or : '*'
        # WHERE statement must be in SQL format: """WHERE 'name' = 'John Doe' """
        # or : '*'

        query = """
        SELECT {} FROM wire_train {};
        """.format(columns,where)

        self.DBCursor.execute(query)






class frontend_DB(BBDB):
    def __init__(self, dbhost : str):

        BBDB.__init__(self, dbhost, 'frontend', 'K6i0aI6cbV2inmuyK4SN')

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

        users = self.getUsers()
        new_uuid = uuid.uuid1()

        for existing_uuid in users:
            while existing_uuid == new_uuid:
                new_uuid = uuid.uuid4()



        query = """
        INSERT INTO shared.user_table (USER_UUID,USERNAME) VALUES('{}','{}');

        """.format(new_uuid,username)

        try:

            self.DBCursor.execute(query)

        except (psy.errors.UniqueViolation):

            raise UsernameExists("Username in use!")


        return True

class UsernameExists(Exception):
    pass







try:
    #x = BBDB('h2938366.stratoserver.net','backend','NfPNlXBcYtIATJIGcuIR')
    #x.testThisClass()
    #x.closeGraceful()
    x = frontend_DB('h2938366.stratoserver.net')
    #x.register_user("John Doe")
    #print(x.getUsers())
    y = wire_DB('h2938366.stratoserver.net')

except Exception as e:

    traceback.print_exc()

    x.closeGraceful()
