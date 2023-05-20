"""
TODO
"""
# TODO: Add a description of the module

from flask_login import UserMixin
import base64
import io
from PIL import Image
import numpy as np
import pickle


class BigBrotherUser(UserMixin):
    """
    This class keeps the information about the user
    """

    # TODO: Find out the types 
    def __init__(self, user_uuid, name, DB):

        self.uuid = user_uuid
        if type(user_uuid) == tuple:
            self.uuid = user_uuid[0]

        self.name = name

        self.trainingPictures = []
        """ logData: Used for logs. Stores past login dates as well as
        the picture IDs that are associated with those logins that came
        from the user with the uuid: self.uuid"""
        self.logData = []
        self.trainingPicturesWebsiteFormat = []
        self.DB = DB

        self.admin = False
        self.childUser = []

        self.sync()

        self.recogFlag = False

    def sync(self):
        pics, uuids = self.DB.getTrainingPictures("WHERE user_uuid = '{}'".format(self.uuid))
        self.trainingPicturesWebsiteFormat = []

        for pic_index,pic in enumerate(pics):
            try:
                if pic.shape[0] == 0 or pic.shape[1] == 0:
                    pic = np.random.randint(255, size=(10,10,3),dtype=np.uint8)

                file_object = io.BytesIO()
                img= Image.fromarray(pic.astype('uint8'))
                img.save(file_object, 'PNG')
                base64img = "data:image/png;base64,"+base64.b64encode(file_object.getvalue()).decode('ascii')
                self.trainingPicturesWebsiteFormat.append((uuids[pic_index],base64img))
                self.trainingPictures.append((uuids[pic_index],pic))
            except ValueError:
                print("Illegal Image Loaded!")
                #print(format("User: {}\n UUID: {}\npic_uuid: {}", self.name,self.uuid,uuids[pic_index]))
                print("User: {}\n UUID: {}\npic_uuid: {}".format(self.name,self.uuid,uuids[pic_index]))
                print(pic.astype('uint8'))
                print(pic.astype('uint8').shape)
                return

        # TODO: Implement the same functionality in mongoDB
        # This is only the log data associated to self.uuid
        '''
        self.DB.DBCursor.execute("SELECT login_date, inserted_pic_uuid FROM shared.login_table WHERE user_uuid = '{}'".format(self.uuid))
        try:
            self.logData = self.DB.DBCursor.fetchall()
        except Exception:
            return

        for row_index, row in enumerate(self.logData):
            print(self.logData[row_index][0])
            self.logData[row_index] = [self.logData[row_index][0].strftime("%d/%m/%Y, %H:%M:%S"),row[1]]
        '''

        # TODO: Implement the same functionality in mongoDB
        '''
        self.childUser = []
        query = """
        SELECT * FROM shared.admin_table;
        """
        self.DB.DBCursor.execute(query)

        ret = self.DB.DBCursor.fetchall()

        for dbTuple in ret:
            if dbTuple[0] == str(self.uuid):
                self.admin = True
                self.childUser.append(dbTuple[1])
        '''

    def get_id(self):
        return self.uuid

