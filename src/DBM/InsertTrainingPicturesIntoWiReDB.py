"""
This is a script used for automatically inserting pictures into the 
WiRe Database. This should be used to initialize the database. 
This would make the visualizations in the Benchmarktests more meaningful.
"""

from sklearn.datasets import fetch_lfw_people
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt
import numpy as np
from PIL import Image
import typing

from DatabaseManagement import wire_DB

# Constants that you can set
MIN_PICS_EACH_USER = 20
## This switch prevents you from inserting into the database if it is set 
## to False. In case you didn't intend to execute this script, because
## it might mess up things in the database
SAFETY_SWITCH = False

if not SAFETY_SWITCH:
    print("Go into the code and change the SAFETY_SWITCH to True if you want to execute this script")
    exit()

dataset = fetch_lfw_people(
        min_faces_per_person=MIN_PICS_EACH_USER,
        resize=1
    )

imgs = dataset.images
targets = dataset.target
target_names = dataset.target_names

# Resize images
resizedImgs = []
image_shape = imgs[0].shape
for img in imgs:
    resizedImgs.append(
            img.reshape(image_shape[1] * image_shape[0])
        )

# structure names
names_to_img_list = {}
for i, target in enumerate(targets):
    name = target_names[target]
    if name not in names_to_img_list:
        names_to_img_list[name] = []
    names_to_img_list[target_names[target]].append(imgs[i])

# insert into database
DB = wire_DB()
for name in names_to_img_list.keys():
    # TODO: add user encoding later
    uuid = DB.register_user(name, None)
    for img in names_to_img_list[name]:
        DB.insertTrainingPicture(img, uuid)

#PIL_image = Image.fromarray(imgs[0].astype('uint8'))
#PIL_image.save("test.png")
