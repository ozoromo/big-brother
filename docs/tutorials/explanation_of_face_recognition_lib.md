# Face-recognition
The purpose of "Face-recognition" is to determine whether two images show the
same person. 

## FaceReco_class
If there is the same person in two images, the program returns the Boolean
value "TRUE", otherwise "FALSE".
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
    - The function takes three parameters: self, image_encoding (encoding of a
      photo saved in the database), and img2 (image captured from a camera).
    - We start with converting img2 to the RGB color space, using the OpenCV
      library. 
    - Then we use face_recognition library to compute encodings for img2 (these
      encodings are numerical representations of the facial features )
    - If no face encodings are detected in the img2, the function returns
      "False"-value.
    - If at least one face encoding is detected in the img2, we compare the
      facial encoding of img2 with the image_encoding (encoding from database)
      using the face_recognition.compare_faces function.
    - This function determines whether the two face encodings belong to the
      same person.
    - We calculate face distance using the face_recognition.face_distance
      function. This distance is a measure of similarity between the two facial
      encodings. A smaller value indicates a greater similarity between the
      faces.
    - Method returns the results list (with True or False indicating if it's
      the same person)
      
- More inforamtion
    - We wrote this code with threads, hoping to optimise program, but eventually gave up on this idea - right server did the job
       
## encodings_class
This code is designed to encode raw face images into encodings that can be used with the face_recognition module. It processes images stored in a directory called "toBeEncoded" and creates suitable encoding files in a directory called "encodings". 
It also removes the original image files after encoding.

- Packages
    - such as for faceReco_class

- What exactly is face encoding?
    - A face encoding is basically a way to represent the face using a set of
      128 computer-generated measurements. Two different pictures of the same
      person would have similar encoding and two different people would have
      totally different encoding.
    - For face encoding we use in our code variable encode, which is a
      numerical representation of the features and characteristics of a
      person's face that is extracted and computed by the face_recognition
      library. The specific type of encode in terms of Python data types is a
      1-dimensional NumPy array. These values from NumPy-array represent the
      facial features in a way that allows for efficient comparison and
      matching. 

- Explanation of code
    - Code retrieves a list of filenames(images) from the "toBeEncoded" folder
      using the os.listdir() function.
    - A loop iterates through each image file in the "toBeEncoded" folder:
    - Image is read using cv2.imread(). The data about image is appended to the
      images list. The class name is extracted from the filename using
      os.path.splitext() and appended to the classNames list.
    - A function findEncodings(images, classNames) is defined to loop through
      the images, their class names and call the findEncoding() function for
      each of them.
    - The findEncoding(img, name, idx) function takes an image, class name, and
      index as parameters. The image is converted to RGB color space using
      cv2.cvtColor(). The facial encoding of the image is computed using
      face_recognition.face_encodings().
    - The addToEncodings() function is called to save the encoding to a file in
      the "encodings" folder. The original image file is removed from
      "toBeEncoded" folder using os.remove().

- Problems
    - The problem may arise when more than one face is recognized in a single
      photo. It may happen then that the calculated encodings are not
      for the person who wants to log in/register, but for example for the face
      on the t-shirt of the person logging in. 
      
### example_usage_FaceReco_class
A code named example_usage_FaceReco_class is basically just an example of using
a previously written FaceReco_class.

## Sources
- https://medium.com/@ageitgey/machine-learning-is-fun-part-4-modern-face-recognition-with-deep-learning-c3cffc121d78   
- https://www.youtube.com/watch?v=iBomaK2ARyI
- https://www.youtube.com/watch?v=sz25xxF_AVE
- Python packet - face_recognition: Here is a description in german:
Das Python-Paket "face-recognition" ist eine Open-Source-Bibliothek, die auf der 
Grundlage von OpenCV entwickelt wurde und auf der Gesichtserkennungstechnologie von dlib basiert. 
Sie ermöglicht die Erkennung und Analyse von Gesichtern in Bildern und Videos.

Die Gesichtserkennungstechnologie von dlib basiert auf dem 2017
veröffentlichten "Histogram of Oriented Gradients for Human Detection"
(HOG)-Feature-Extractor und dem "Linear Support Vector Machines"
(SVM)-Klassifikator. Diese Methode wurde von Navneet Dalal und Bill Triggs in
ihrer Veröffentlichung "Histograms of Oriented Gradients for Human Detection"
vorgestellt.

Die dlib-Bibliothek verwendet eine Kombination aus HOG-Features und
SVM-Klassifikation, um Gesichter in Bildern zu erkennen. Der HOG-Algorithmus
basiert auf der Idee, dass das Erscheinungsbild eines 		Objekts durch die
Verteilung von Gradienten oder Kanteninformationen beschrieben werden kann. Es
werden Histogramme der Gradientenrichtungen erstellt und diese Histogramme
dienen als Features für den 	Klassifikator.

Der SVM-Klassifikator wird trainiert, um zwischen Gesichts- und
Nicht-Gesichtsregionen zu unterscheiden. Dafür werden positive Beispiele von
Gesichtern und negative Beispiele von Nicht-Gesichtern 		verwendet. Der
SVM-Klassifikator lernt dann, diese beiden Klassen zu unterscheiden und kann
anschließend auf neue Bilder angewendet werden, um Gesichter zu erkennen.

Die dlib-Bibliothek stellt auch eine vortrainierte
Gesichtserkennungsmodell-Datei bereit, die mit dem HOG-Feature-Extractor und
dem SVM-Klassifikator trainiert wurde. Dieses Modell wird verwendet, um
Gesichter zu erkennen und kann mit der Funktion
`dlib.get_frontal_face_detector()` abgerufen werden.

Quellen:
- N. Dalal and B. Triggs, "Histograms of Oriented Gradients for Human Detection," 2005 IEEE Computer Society Conference on Computer Vision and Pattern Recognition (CVPR'05), San Diego, CA, USA, 2005, pp. 886-893, doi: 10.1109/CVPR.2005.177.
- Dlib Library Documentation: http://dlib.net/face_detection.py.html
- https://pypi.org/project/face-recognition/
