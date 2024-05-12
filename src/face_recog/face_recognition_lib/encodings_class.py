import cv2
import numpy as np
import face_recognition
import os


"""
Script to encode raw images into encodings capable for the 'face_recognition' module


Instructions:

BEFORE USAGE:
- Create Folder 'toBeEncoded' in the same directory
- Create Folder 'encodings' in the same directory

USAGE:
- put face pictures in the folder 'toBeEncoded' (jpg or png)
- start the script

"""


path = "toBeEncoded"
encodingsPath = "encodings"
images = []
classNames = []
fileList = os.listdir(path)
encodingsList = ""
print(fileList)

for cls in fileList:
    curImg = cv2.imread(f"{path}/{cls}")
    images.append(curImg)
    classNames.append(os.path.splitext(cls)[0])

print(classNames)

def findEncodings(images, classNames):
    idx = 0
    for img, cls in zip(images, classNames):
        findEncoding(img, cls, idx)
        idx += 1

def findEncoding(img, name, idx):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encode = face_recognition.face_encodings(img)[0]
    #print(encode)
    addToEncodings(encode, name)
    os.remove(f"{path}/{fileList[idx]}")

def addToEncodings(encode, name):
    encode.tofile(f"{encodingsPath}/{name}")

def readFromEncodings(name):
    encode = np.fromfile(f"{encodingsPath}/{name}")
    return encode


findEncodings(images, classNames)
