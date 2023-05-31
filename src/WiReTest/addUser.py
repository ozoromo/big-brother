import numpy as np
import lib
import matplotlib as mpl
import DatabaseManagement
import uuid


DB = DatabaseManagement.wire_DB('h2938366.stratoserver.net')

#user_uuid = DB.register_user("jonny_sins")
print("start")

images = []

# TODO read each image in path as numpy.ndarray and append to images
# Useful functions: lib.list_directory(), matplotlib.image.imread(), numpy.asarray()
path = "./jonny_cut/"

img_str_list = lib.list_directory(path)

for img_str in sorted(img_str_list):
    print("test")

    if img_str[-3:] != "png":

        #raise ValueError("Incorrect Data Type")

        continue

    im_path = path + img_str

    image = np.asarray(mpl.image.imread(im_path), dtype=np.float64)

    user_uuid = None

    print("test2")

    try:

        user_uuid = DB.register_user("jonny_sins")
        print("Created User : {} with uuid : {} ".format(img_str[0:2],user_uuid))

    except DatabaseManagement.UsernameExists:

        users = DB.getUsers()

        for u_uuid in users:

            if users[u_uuid] == "jonny_sins":
                user_uuid = u_uuid

    print("test3")

    if not user_uuid:
        raise BaseException("No user id given")

    if type(user_uuid) == str:
        user_uuid = uuid.UUID(user_uuid)

    print("test4")
    pic_uuid = DB.insertTrainingPicture(image,user_uuid)
    print("inserted : {}\nwith uuid : {}\nand user uuid : {}\n\n\n".format(img_str,pic_uuid,user_uuid))
DB.closeGraceful()
