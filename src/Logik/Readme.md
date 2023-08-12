# Logik-Group Documentation 
## Face-recognition
The purpose of "Face-recognition" is to determine whether two images show the same person. 
- During the work we based on article and two youtube videos:
    - https://medium.com/@ageitgey/machine-learning-is-fun-part-4-modern-face-recognition-with-deep-learning-c3cffc121d78   
    - https://www.youtube.com/watch?v=iBomaK2ARyI
    - https://www.youtube.com/watch?v=sz25xxF_AVE
### FaceReco_class
If there is the same person in two images, the program returns the Boolean value "TRUE", otherwise "FALSE".
- Download
    - Python Version: 3.11   
    - https://visualstudio.microsoft.com/downloads/
    - Packages
        - cmake
        - dlib
        - face-recognition
        - numpy
        - opencv-python
          
- Explanation of code 
    - The function takes three parameters: self, image_encoding (encoding of a photo saved in the database), and img2 (image captured from a camera).
    - We start with converting img2 to the RGB color space, using the OpenCV library. 
    - Then we use face_recognition library to compute encodings for img2 (these encodings are numerical representations of the facial features )
    - If no face encodings are detected in the img2, the function returns "False"-value.
    - If at least one face encoding is detected in the img2, we compare the facial encoding of img2 with the image_encoding (encoding from database) using the face_recognition.compare_faces function.
    - This function determines whether the two face encodings belong to the same person.
    - We calculate face distance using the face_recognition.face_distance function. This distance is a measure of similarity between the two facial encodings. A smaller value indicates a greater similarity between the faces.
    - Method returns the results list (with True or False indicating if it's the same person)
      
- More inforamtions
    - We wrote this code with threads, hoping to optimise program, but eventually gave up on this idea - right server did the job
       
### encodings_class
This code is designed to encode raw face images into encodings that can be used with the face_recognition module. It processes images stored in a directory called "toBeEncoded" and creates suitable encoding files in a directory called "encodings". 
It also removes the original image files after encoding.

- Packages
    - such as for faceReco_class

- Explanation of code
    - Code retrieves a list of filenames(images) from the "toBeEncoded" folder using the os.listdir() function.
    - A loop iterates through each image file in the "toBeEncoded" folder:
    - Image is read using cv2.imread(). The data about image is appended to the images list.
      The class name is extracted from the filename using os.path.splitext() and appended to the classNames list.
    - A function findEncodings(images, classNames) is defined to loop through the images, their class names and call the findEncoding() function for each of them.
    - The findEncoding(img, name, idx) function takes an image, class name, and index as parameters. The image is converted to RGB color space using cv2.cvtColor().
    The facial encoding of the image is computed using face_recognition.face_encodings().
    - The addToEncodings() function is called to save the encoding to a file in the "encodings" folder. The original image file is removed from "toBeEncoded" folder using os.remove().
  
### example_usage_FaceReco_class
A code named example_usage_FaceReco_class is basically just an example of using a previously written FaceReco_class.
## Gesture-recognition
