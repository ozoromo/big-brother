# @Author: Julius U. Heller
# @Date:   2021-06-20T14:04:47+02:00
# @Project: ODS-Praktikum-Big-Brother
# @Filename: user.py
# @Last modified by:   Julius U. Heller
# @Last modified time: 2021-06-20T14:43:25+02:00
from flask_login import UserMixin
import base64
import io
from PIL import Image
import numpy as np
import pickle


class BigBrotherUser(UserMixin):

    def __init__(self,user_uuid,name,DB):

        self.uuid = user_uuid

        if type(user_uuid) == tuple:
            self.uuid = user_uuid[0]

        self.name = name

        self.trainingPictures = []
        self.logData = []
        self.trainingPicturesWebsiteFormat = []
        self.DB = DB

        self.admin = False
        self.childUser = []

        self.sync()



        self.recogFlag = False

        #self.is_authenticated = False

        #self.is_active = True
        #self.is_anonymous = False

    def sync(self):

        pics, uuids = self.DB.getTrainingPictures("WHERE user_uuid = '{}'".format(self.uuid))
        #self.DB.DBCursor.execute("SELECT pic_uuid, pic_data FROM wire_train_pictures WHERE user_uuid = '{}'".format(self.uuid))
        #self.trainingPictures = self.DB.DBCursor.fetchall()

        self.trainingPicturesWebsiteFormat = []

        for pic_index,pic in enumerate(pics):

            try:

                if pic.shape[0] == 0 or pic.shape[1] == 0:
                    #pic = np.random.randint(255, size=(pic.shape[0],pic.shape[1],3),dtype=np.uint8)
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
                #pass
                #continue

        self.DB.DBCursor.execute("SELECT login_date, inserted_pic_uuid FROM shared.login_table WHERE user_uuid = '{}'".format(self.uuid))
        try:
            self.logData = self.DB.DBCursor.fetchall()
        except Exception:
            return

        for row_index, row in enumerate(self.logData):
            print(self.logData[row_index][0])
            self.logData[row_index] = [self.logData[row_index][0].strftime("%d/%m/%Y, %H:%M:%S"),row[1]]


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
        print(self.childUser)





    def get_id(self):
        return self.uuid
