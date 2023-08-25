# Ultra light and openface
Below there are some sources with information that was extracted from those
sources.

## 1. https://medium.com/@ageitgey/machine-learning-is-fun-part-4-modern-face-recognition-with-deep-learning-c3cffc121d78
Step 1: Finding all Faces
    - Using Histogram of Oriented Gradients (HOG)
    - Create a gradient map (look at 16x16 pixels and determine in which direction the pixels are getting darker)
    - End result can be compared to a specific HOG pattern, if it matches, then the algorithm has detected a face
Step 2: Posing and Projecting Faces
    - Algorithm called face landmark estimation uses a set of specific points that exist on every face
    - Through machine learning, the program will be able to find these landmarks on every face
    - Once found, it will rotate and scale the picture to make the face match the template landmarks to make it easier to compare it to other faces
Step 3: Encoding faces
    - Train a neural network to recognize 128 measurements on each face
    - Single training step: pictures 1 & 2 are the same perso but different picture, picture 3 is a different person
    - Train it to make the measurement of 1 & 2 slightly closer together and 2 & 3 slightly more apart
    - Takes long time to get a good accuracy (more that 24 hours of continuous training)
Step 4: Find the person
    - Find Person in our database that matches the measurements the most

## 2. https://github.com/cmusatyalab/openface
## 3. https://towardsdatascience.com/real-time-face-recognition-with-cpu-983d35cc3ec5
## 4. https://sefiks.com/2019/07/21/face-recognition-with-openface-in-keras/
- OpenFace incompatible with PyTorch, that’s why Keras-OpenFace repository needs to be used, but restricted to specific Keras version
- Load the image and pre-trained weights
- Different photos of same person should have low distance but of different person have hight distance
- Distances can be measure by comparing cosine and euclidian distances of each picture and setting a threshhold (e.g. 0.02 cosine and 0.20 euclidian)
- Face detection and alignment with between 68 and 468 landmarks

## 5. https://cmusatyalab.github.io/openface/
- Just Openface

## 6. https://medium.com/analytics-vidhya/face-recognition-using-openface-92f02045ca2a
1. Isolating a face from background, isolating a single face from several different ones found in the same photo
    - deal with bad and inconsistent lightning and various facial positions
    - image with face bounded ractangle
    - solution: dlib over opencv's Harr cascade classifier: speed, implementation and accuracy 
    - we are already using dlib
2. Projection of face
    - the face on two different photos differs in position, try to do so that the eyes and mouth (by them programm recognize that something is a face) are always in the same place on the image - this will make it 
     easier to compare faces)
    - train a machine-learning algorithm to be able to find 68 specific points on any face (selecting points exactly how with hands)
     these landmarks in every face, simply rotate and scale the image so that the eyes and mouth are centered as best as possible
3. Open face (implementation)
    - After isolate the image from the background and preprocess it using dlib, find a way to represent the face in numerical embedding. Represent it using a pre-trained deep neural network OpenFace 
4. Triplet loss function
    - Neural networks need to be trained in such a way that embedding of anchor image(basic photo of Person X) and positive image(zphoto of Person A) 
     should be similar and embedding of anchor image and negative image(photo of Person Y) should be much farther apart.
5. Training and Classification a face recognition model
    - To compare two images, create the embedding for both images by feeding through the model separately. Use Euclidean distance to find the distance which will be lower value for similar faces and higher valuefor 
     different faces.

