###############################################
#         Make THIS script executable         #
###############################################
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "gesture_recognition"))

###############################################
#       The actual program starts here        #
###############################################
import cv2
from gesture_recognizer import GestureRecognizer


cap = cv2.VideoCapture(0)
recognizer = GestureRecognizer()

while True:
    _, frame = cap.read()
    frame, class_name = recognizer.recognize(frame)

    # show the prediction on the frame
    cv2.putText(frame, class_name, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 0, 255), 2, cv2.LINE_AA)

    # Show the final output
    cv2.imshow("Output", frame)

    if cv2.waitKey(1) == ord('q'):
        break

# release the webcam and destroy all active windows
cap.release()
cv2.destroyAllWindows()
