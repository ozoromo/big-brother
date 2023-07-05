import cv2
import GestureReco_class


cap = cv2.VideoCapture(0)
g = GestureReco_class.GestureReco()
#f = FaceReco_class.FaceReco()

while True:
    _, frame = cap.read()
    frame, className = g.read_each_frame_from_webcam(frame)
    #print(className)

    # show the prediction on the frame
    cv2.putText(frame, className, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 0, 255), 2, cv2.LINE_AA)
    # STEP 5 - END

    # Show the final output
    cv2.imshow("Output", frame)

    if cv2.waitKey(1) == ord('q'):
        break

# release the webcam and destroy all active windows
cap.release()
cv2.destroyAllWindows()