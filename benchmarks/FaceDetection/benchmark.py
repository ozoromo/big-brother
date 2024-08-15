import cv2
from mtcnn import MTCNN
import time
import matplotlib.pyplot as plt
import face_recognition
import numpy as np
import dlib

from skimage import io, color
from skimage.feature import hog
from skimage import exposure

from ultra_light import FaceDetection

"""
    Haar Cascade is a machine learning-based approach used for object detection, 
    specifically designed for face detection but applicable to various object detection 
    tasks.

    The method involves training a classifier with a large number of positive (object) 
    and negative (non-object) images. We use cv2.data.haarcascades pre-trained data set.
"""
def detect_faces_haar_default(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return faces

"""
    In this alternative Haar Cascade we use another pre-trained Haar Cascade classifier provided
    by OpenCV for face detection. 
"""
def detect_faces_haar_alt2(image):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
    faces = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5)
    return faces

"""
    The face_recognition library uses the Histogram of Oriented Gradients (HOG) 
    or Convolutional Neural Network (CNN) models from the dlib library to locate faces.

    By default uses HOG for face detection, can be switched to CNN to the more accurate (but slower)
    CNN model with face_recognition.face_locations(img, model='cnn')
"""
def detect_faces_face_recognition(image):
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image)
    faces = [(left, top, right-left, bottom-top) for top, right, bottom, left in face_locations]
    return faces

"""
    MTCNN or Multi-Task Cascaded Convolutional Neural Networks is a neural network 
    which detects faces and facial landmarks on images.
"""
def detect_faces_mtcnn(image):
    detector = MTCNN()
    results = detector.detect_faces(image)
    faces = [(result['box'][0], result['box'][1], result['box'][2], result['box'][3]) for result in results]
    return faces

"""
    In the context of face detection, ultra-light models aim to provide accurate face detection 
    with minimal computational overhead.

    In this type of ultra-light face detection we use ultra_light_640.onnx model to locate faces.
"""
def detect_faces_ultra_light(image):
    # preprocess img acquired
    img = cv2.imread(image)
    h, w, _ = img.shape
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (640, 480)) 
    img_mean = np.array([127, 127, 127])
    img = (img - img_mean) / 128
    img = np.transpose(img, [2, 0, 1])
    img = np.expand_dims(img, axis=0)
    img = img.astype(np.float32)

    # load the model, create runtime session & get input variable name
    ultra_light_detector = FaceDetection()

    confidences, boxes = ultra_light_detector.ort_session.run(None, {input_name: img})
    boxes, labels, probs = ultra_light_detector.predict(w, h, confidences, boxes, 0.7)

    return boxes, labels, probs

def benchmark(model, image_path, num_iterations=1):
    times = []
    num_faces = []
    
    for _ in range(num_iterations):
        image = cv2.imread(image_path)
        start_time = time.time()
        faces = model(image)
        end_time = time.time()
        
        times.append(end_time - start_time)
        num_faces.append(len(faces))
        
    return times, num_faces, faces

def draw_faces(image, faces):
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
    return image

def draw_faces_ult(image, labels, boxes):
    for i in range(boxes.shape[0]):
        box = boxes[i, :]
        x1, y1, x2, y2 = box
        cv2.rectangle(image, (x1, y1), (x2, y2), (80,18,236), 2)
        cv2.rectangle(image, (x1, y2 - 20), (x2, y2), (80,18,236), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        text = f"face: {labels[i]}"
        cv2.putText(image, text, (x1 + 6, y2 - 6), font, 0.5, (255, 255, 255), 1)

def main():
    testing = 1
    image_path = 'test_images/Bild_4.jpg'
    if testing == 1:

        models = [
            detect_faces_haar_default,
            detect_faces_haar_alt2,
            detect_faces_face_recognition,
            detect_faces_mtcnn
        ]

        haar_default_time, haar_default_faces_detected, haar_default_faces = benchmark(models[0], image_path)
        haar_alt2_time, haar_alt2_faces_detected, haar_alt2_faces = benchmark(models[1], image_path)
        face_recog_time, face_recog_faces_detected, face_recog_faces = benchmark(models[2], image_path)
        mtcnn_time, mtcnn_faces_detected, mtcnn_num_faces = benchmark(models[3], image_path)

        print("Haar Default model:")
        print("Average Time per Iteration:", haar_default_time, "seconds")
        print("Average Faces Detected per Iteration:", haar_default_faces_detected)

        print("\nHaar Alt2 model:")
        print("Average Time per Iteration:", haar_alt2_time, "seconds")
        print("Average Faces Detected per Iteration:", haar_alt2_faces_detected)

        print("\nFace Recognition model:")
        print("Average Time per Iteration:", face_recog_time, "seconds")
        print("Average Faces Detected per Iteration:", face_recog_faces_detected)

        print("\nMTCNN model:")
        print("Average Time per Iteration:", mtcnn_time, "seconds")
        print("Average Faces Detected per Iteration:", mtcnn_faces_detected)

        # Plot the results
        fig, axs = plt.subplots(2, 1, figsize=(10, 8))
        axs[0].plot(haar_default_time, label='Haar Default', color='blue')
        axs[0].plot(haar_alt2_time, label='Haar Alt2', color='green')
        axs[0].plot(face_recog_time, label='Face Recognition', color='red')
        axs[0].plot(mtcnn_time, label='MTCNN', color='purple')
        axs[0].set_title('Time taken for Face Detection')
        axs[0].set_xlabel('Iteration')
        axs[0].set_ylabel('Time (seconds)')
        axs[0].legend()

        axs[1].plot(haar_default_faces_detected, label='Haar Default', color='blue')
        axs[1].plot(haar_alt2_faces_detected, label='Haar Alt2', color='green')
        axs[1].plot(face_recog_faces_detected, label='Face Recognition', color='red')
        axs[1].plot(mtcnn_faces_detected, label='MTCNN', color='purple')
        axs[1].set_title('Number of Faces Detected')
        axs[1].set_xlabel('Iteration')
        axs[1].set_ylabel('Number of Faces')
        axs[1].legend()

        plt.tight_layout()
        plt.show()

        # Visualize detected faces on the image
        image_haar_default = cv2.imread(image_path)
        image_haar_alt2 = cv2.imread(image_path)
        image_face_recog = cv2.imread(image_path)
        image_face_mtcnn = cv2.imread(image_path)

        image_haar_default = draw_faces(image_haar_default, haar_default_faces)
        image_haar_alt2 = draw_faces(image_haar_alt2, haar_alt2_faces)
        image_face_recog = draw_faces(image_face_recog, face_recog_faces)
        image_face_mtcnn = draw_faces(image_face_mtcnn, mtcnn_num_faces)

        # Convert images to RGB for displaying with matplotlib
        image_haar_rgb = cv2.cvtColor(image_haar_default, cv2.COLOR_BGR2RGB)
        image_alt2_lrgb = cv2.cvtColor(image_haar_alt2, cv2.COLOR_BGR2RGB)
        image_face_recog_rgb = cv2.cvtColor(image_face_recog, cv2.COLOR_BGR2RGB)
        image_face_mtcnn_rgb = cv2.cvtColor(image_face_mtcnn, cv2.COLOR_BGR2RGB)

        fig, axs = plt.subplots(1, 4, figsize=(15, 7))
        axs[0].imshow(image_haar_rgb)
        axs[0].set_title('Haar default Faces Detected\nNumber of Faces = {}'.format(len(haar_default_faces)))
        axs[0].axis('off')

        axs[1].imshow(image_alt2_lrgb)
        axs[1].set_title('Haar alt2 Faces Detected\nNumber of Faces = {}'.format(len(haar_alt2_faces)))
        axs[1].axis('off')

        axs[2].imshow(image_face_recog_rgb)
        axs[2].set_title('Face Recognition Faces Detected\nNumber of Faces = {}'.format(len(face_recog_faces)))
        axs[2].axis('off')

        axs[3].imshow(image_face_mtcnn_rgb)
        axs[3].set_title('MTCNN Faces Detected\nNumber of Faces = {}'.format(len(mtcnn_num_faces)))
        axs[3].axis('off')


        plt.tight_layout()
        plt.show()
    elif testing == 2:
        image_face_ult = cv2.imread(image_path)
        boxes, labels, probs  = detect_faces_ultra_light(image=image_face_ult)
        draw_faces_ult(image=image_face_ult, labels=labels, boxes=boxes)
        cv2.imshow('Video', image_face_ult)
    elif testing == 3:
        original_image = io.imread(image_path)
        image = io.imread(image_path, as_gray=True)
        hog_features, hog_image = hog(image, 
                              pixels_per_cell=(8, 8),
                              cells_per_block=(2, 2),
                              visualize=True)
        hog_image_rescaled = exposure.rescale_intensity(hog_image, in_range=(0, 10))

        plt.subplot(1, 2, 1)
        plt.imshow(original_image)
        plt.title("Original Image")
        plt.axis('off')

        plt.subplot(1, 2, 2)
        plt.imshow(hog_image_rescaled, cmap='gray')
        plt.title("HOG Features")
        plt.axis('off')

        plt.show()




if __name__ == "__main__":
    main()