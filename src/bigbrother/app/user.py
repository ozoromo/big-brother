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
from pymongo import MongoClient


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
"""
        # TODO Fix
        # Log-Daten aus MongoDB abrufen
        login_collection = self.DB['login_table']
        query = {"user_uuid": str(self.uuid)}
        result = login_collection.find(query)
        
        self.logData = []
        for document in result:
            login_date = document['login_date'].strftime("%d/%m/%Y, %H:%M:%S")
            inserted_pic_uuid = document['inserted_pic_uuid']
            self.logData.append([login_date, inserted_pic_uuid])
            
        # Child-User aus MongoDB abrufen
        admin_collection = self.DB['admin_table']
        query = {"admin_uuid": str(self.uuid)}
        result = admin_collection.find(query)

        self.childUser = []
        for document in result:
            child_user = document['child_user']
            self.admin = True
            self.childUser.append(child_user)
       
    def get_id(self):
        return self.uuid"""

