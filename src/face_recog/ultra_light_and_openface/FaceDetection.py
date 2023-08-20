from operator import ne
import cv2
import numpy as np
from numpy.linalg import norm
import onnx
import onnxruntime as ort
from onnx_tf.backend import prepare
import os, sys
import dlib
from imutils import face_utils
import cv2
import openface
import logging
import platform

"""
Die Datei FaceDetection mithilfe des Blogposts https://towardsdatascience.com/real-time-face-recognition-with-cpu-983d35cc3ec5
nachprogrammiert. Alle Funktionen funktionieren nach Plan, die Gesichter werden erkannt und mit einer Box umrahmt.
Probleme macht die Funktion @get_boxes da die Box als Liste in einer Liste [[1 2 3 4]] zurückgegeben wird und dadurch die Funktion
@face_align in FaceAlign.py nicht damit umgehen kann.

#TODO
Konstruktor erstellen der alles was im Ordner "Models" zu finden ist initialisiert

"""

net = None


def area_of(left_top, right_bottom):
    """
    Compute the areas of rectangles given two corners.
    Args:
        left_top (N, 2): left top corner.
        right_bottom (N, 2): right bottom corner.
    Returns:
        area (N): return the area.
    """
    hw = np.clip(right_bottom - left_top, 0.0, None)
    return hw[..., 0] * hw[..., 1]


def iou_of(boxes0, boxes1, eps=1e-5):
    """
    Return intersection-over-union (Jaccard index) of boxes.
    Args:
        boxes0 (N, 4): ground truth boxes.
        boxes1 (N or 1, 4): predicted boxes.
        eps: a small number to avoid 0 as denominator.
    Returns:
        iou (N): IoU values.
    """
    overlap_left_top = np.maximum(boxes0[..., :2], boxes1[..., :2])
    overlap_right_bottom = np.minimum(boxes0[..., 2:], boxes1[..., 2:])

    overlap_area = area_of(overlap_left_top, overlap_right_bottom)
    area0 = area_of(boxes0[..., :2], boxes0[..., 2:])
    area1 = area_of(boxes1[..., :2], boxes1[..., 2:])
    return overlap_area / (area0 + area1 - overlap_area + eps)


def hard_nms(box_scores, iou_threshold, top_k=-1, candidate_size=200):
    """
    Perform hard non-maximum-supression to filter out boxes with iou greater
    than threshold
    Args:
        box_scores (N, 5): boxes in corner-form and probabilities.
        iou_threshold: intersection over union threshold.
        top_k: keep top_k results. If k <= 0, keep all the results.
        candidate_size: only consider the candidates with the highest scores.
    Returns:
        picked: a list of indexes of the kept boxes
    """
    scores = box_scores[:, -1]
    boxes = box_scores[:, :-1]
    picked = []
    indexes = np.argsort(scores)
    indexes = indexes[-candidate_size:]
    while len(indexes) > 0:
        current = indexes[-1]
        picked.append(current)
        if 0 < top_k == len(picked) or len(indexes) == 1:
            break
        current_box = boxes[current, :]
        indexes = indexes[:-1]
        rest_boxes = boxes[indexes, :]
        iou = iou_of(
            rest_boxes,
            np.expand_dims(current_box, axis=0),
        )
        indexes = indexes[iou <= iou_threshold]

    return box_scores[picked, :]


def predict(width, height, confidences, boxes, prob_threshold, iou_threshold=0.5, top_k=-1):
    """
    Select boxes that contain human faces
    Will take in an array of Boxes and their corresponding confidence level for each labels.
    Filtering by confidence will then be performed to retain all the boxes wit high probability
    of containing a face.
    Args:
        width: original image width
        height: original image height
        confidences (N, 2): confidence array
        boxes (N, 4): boxes array in corner-form
        iou_threshold: intersection over union threshold.
        top_k: keep top_k results. If k <= 0, keep all the results.
    Returns:
        boxes (k, 4): an array of boxes kept
        labels (k): an array of labels for each boxes kept
        probs (k): an array of probabilities for each boxes being in corresponding labels
    """
    boxes = boxes[0]
    confidences = confidences[0]
    picked_box_probs = []
    picked_labels = []
    for class_index in range(1, confidences.shape[1]):
        probs = confidences[:, class_index]
        mask = probs > prob_threshold
        probs = probs[mask]
        if probs.shape[0] == 0:
            continue
        subset_boxes = boxes[mask, :]
        box_probs = np.concatenate([subset_boxes, probs.reshape(-1, 1)], axis=1)
        box_probs = hard_nms(box_probs,
                             iou_threshold=iou_threshold,
                             top_k=top_k,
                             )
        picked_box_probs.append(box_probs)
        picked_labels.extend([class_index] * box_probs.shape[0])
    if not picked_box_probs:
        return np.array([]), np.array([]), np.array([])
    picked_box_probs = np.concatenate(picked_box_probs)
    picked_box_probs[:, 0] *= width
    picked_box_probs[:, 1] *= height
    picked_box_probs[:, 2] *= width
    picked_box_probs[:, 3] *= height
    return picked_box_probs[:, :4].astype(np.int32), np.array(picked_labels), picked_box_probs[:, 4]


# load the model, create runtime session & get input variable name

onnx_path = os.path.join(os.path.dirname(__file__), 'Model', 'ultra_light_640.onnx')
onnx_model = onnx.load(onnx_path)
predictor = prepare(onnx_model)
ort_session = ort.InferenceSession(onnx_path)
input_name = ort_session.get_inputs()[0].name


def make_rectangle(frame):
    # ret, frame = video_capture.read()

    h, w, _ = frame.shape
    # preprocess img acquired
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (640, 480))  # Resize the Image ultralight 640x480 model
    img_mean = np.array([127, 127, 127])
    img = (img - img_mean) / 128
    img = np.transpose(img, [2, 0, 1])
    img = np.expand_dims(img, axis=0)
    img = img.astype(np.float32)

    confidences, boxes = ort_session.run(None, {input_name: img})  # run onnx

    boxes, labels, probs = predict(w, h, confidences, boxes, 0.7)
    # print(boxes)
    for i in range(boxes.shape[0]):
        box = boxes[i, :]
        x1, y1, x2, y2 = box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (80, 18, 236), 2)
        cv2.rectangle(frame, (x1, y2 - 20), (x2, y2), (80, 18, 236), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        text = f"face: {labels[i]}"
        cv2.putText(frame, text, (x1 + 6, y2 - 6), font, 0.5, (255, 255, 255), 1)
        """
        Cuts the Image to only the face
        h = y2 - y1
        w = x2 -x1
        frame = frame[y1:y1+h, x1:x1+w]
        """

    return frame


def cut_rectangle(frame):
    # ret, frame = video_capture.read()

    h, w, _ = frame.shape
    # preprocess img acquired
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (640, 480))  # Resize the Image ultralight 640x480 model
    img_mean = np.array([127, 127, 127])
    img = (img - img_mean) / 128
    img = np.transpose(img, [2, 0, 1])
    img = np.expand_dims(img, axis=0)
    img = img.astype(np.float32)

    confidences, boxes = ort_session.run(None, {input_name: img})  # run onnx

    boxes, labels, probs = predict(w, h, confidences, boxes, 0.7)
    # print(boxes)
    for i in range(boxes.shape[0]):
        box = boxes[i, :]
        x1, y1, x2, y2 = box
        # cv2.rectangle(frame, (x1, y1), (x2, y2), (80, 18, 236), 2)
        # cv2.rectangle(frame, (x1, y2 - 20), (x2, y2), (80, 18, 236), cv2.FILLED)
        # font = cv2.FONT_HERSHEY_DUPLEX
        # text = f"face: {labels[i]}"
        # cv2.putText(frame, text, (x1 + 6, y2 - 6), font, 0.5, (255, 255, 255), 1)

        # Cuts the Image to only the face
        h = y2 - y1
        w = x2 - x1
        frame = frame[y1:y1 + h, x1:x1 + w]

    #print(frame)
    return frame


def get_boxes(frame):
    # ret, frame = video_capture.read()
    if len(frame.shape) == 2:
        h, w = frame.shape
    else:
        h, w, _ = frame.shape
    # preprocess img acquired
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (640, 480))  # Resize the Image ultralight 640x480 model
    img_mean = np.array([127, 127, 127])
    img = (img - img_mean) / 128
    img = np.transpose(img, [2, 0, 1])
    img = np.expand_dims(img, axis=0)
    img = img.astype(np.float32)

    confidences, boxes = ort_session.run(None, {input_name: img})  # run onnx

    boxes, labels, probs = predict(w, h, confidences, boxes, 0.7)

    return boxes


"""
shape_predictor = dlib.shape_predictor(
    '/Users/dominik/Desktop/University/Semester 4/ODS '
    'Programmierpraktikum/ODS-Praktikum-Big-Brother/FaceRecognition/Model/shape_predictor_68_face_landmarks.dat')
fa = face_utils.FaceAligner(shape_predictor, desiredFaceWidth=112, desiredLeftEye=(0.3, 0.3))


@:param box: von der Funktion @get_boxes in FaceDetection übergebene Box um das Gesicht wird als Argument
übergeben und das aligned_face (eingeteilt in die 68 Landmarks eines Gesichts siehe Projection of Face in
https://medium.com/analytics-vidhya/face-recognition-using-openface-92f02045ca2a) wird returned.

def face_align(box, raw_img):
    # convert face to grayscale

    x1, y1, x2, y2 = box
    gray = cv2.cvtColor(raw_img, cv2.COLOR_BGR2GRAY)

    # align the face and resize
    aligned_face = fa.align(raw_img, gray, dlib.rectangle(left=x1, top=y1, right=x2, bottom=y2))
    aligned_face = cv2.resize(aligned_face, (96, 96))  # resize to 96x96 for openface

    return aligned_face
"""

dlibFacePredictor = os.path.join(os.path.dirname(__file__), 'Model', 'shape_predictor_68_face_landmarks.dat')
align = openface.AlignDlib(dlibFacePredictor)


# Test neue align funktion
def aligner(box, raw_img):
    x1 = box[0]
    y1 = box[1]
    x2 = box[2]
    y2 = box[3]

    # landmarks = align.findLandmarks(np.asarray(raw_img),
    # dlib.rectangle(left=x1, top=y1, right=x2, bottom=y2))  # np.asarray nicht nötig?
    landmarks = align.findLandmarks(raw_img,
                                    dlib.rectangle(left=x1, top=y1, right=x2, bottom=y2))  # np.asarray nicht nötig?
    if landmarks is None:
        logging.info("Could not find Facial Landmarks!")
        # print("Could not find Facial Landmarks!")
        return None

    aligned_face = align.align(96, raw_img, bb=dlib.rectangle(left=x1, top=y1, right=x2, bottom=y2),
                               landmarks=landmarks,
                               landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
    if aligned_face is None:
        logging.info("Could not align Face!")
        # print("Could not align Face!")
        return None
    logging.info("Face aligned!")
    return aligned_face


def getRep(aligned_face):
    global net
    bgrImg = aligned_face
    if bgrImg is None:
        logging.error("Unable to load image!")
        return None
    aligned_face = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)
    logging.info("Getting 128 vector representation of face!")
    rep = net.forward(aligned_face)[0]
    return rep


# measure euclidian distance threshold should be around 0.2 to 0.5
def get_euclidian_distance(rep1, rep2):
    # distance = np.sqrt(np.sum((rep1 - rep2) ** 2))
    distance = np.linalg.norm(rep1 - rep2, axis=1)
    return distance


def getDistance(rep1, rep2):
    """Returns number between 0-4, Openface calculated the mean between
            similar faces is 0.99 i.e. returns less than 0.99 if reps both belong
            to the same person"""
    d = rep1 - rep2
    return d


# cosine similarity threshold should be around 0.02 to 0.07
def get_cosine_similarity(rep1, rep2):
    cos_sim = np.dot(rep1, rep2) / (norm(rep1) - norm(rep2))
    return cos_sim


def authorize_user(train_images, test_image, distance=0.65, similarity=0.02, testdistance=0.99):
    init()

    # TODO maybe necessary: crop and align train and test images

    # not normalized training pictures
    # für das eine testbild : jedes trainingsbild vergleichen
    dists = []
    # test_image_box = get_boxes(test_image)
    test_image_box = (0, 0, test_image.shape[1], test_image.shape[0])
    test_image = aligner(test_image_box, test_image)
    test_rep = getRep(test_image)
    for train_img in train_images:
        train_image_box = (0, 0, train_img.shape[1], train_img.shape[0])
        train_img = aligner(train_image_box, train_img)
        train_rep = getRep(train_img)
        dists.append(get_euclidian_distance(train_rep, test_rep))
        # dists.append(getDistance(test_rep, train_rep))

    # den niedrigsten wert auswählen und den mit dem threshold abgleichen
    dists = np.asarray(dists)
    min_dist = np.min(dists)
    print(min_dist)

    result = min_dist <= distance
   # result = min_dist <= testdistance

    return result


def get_dist_from_images(train_image, test_image, distance=0.5, similarity=0.02):
    global net
    if net is None:
        init()

    # TODO maybe necessary: crop and align train and test images

    # not normalized training pictures
    # für das eine testbild : jedes trainingsbild vergleiche
    test_rep = getRep(test_image)
    train_rep = getRep(train_image)

    return get_euclidian_distance(train_rep, test_rep)


def init():
    global net
    imgDim = 96
    if net is None and (platform.system() == 'Linux' or platform.system() == "Darwin"):
        net = openface.TorchNeuralNet(os.path.join(os.path.dirname(__file__), 'Model', 'nn4.small2.v1.t7'), imgDim)


if __name__ == "__main__":
    '''imgDim = None
    openfaceDir = os.path.join(os.path.dirname(__file__), 'Model', 'nn4.small2.v1.t7')
    net = None

    if platform.system() == 'Linux':
        imgDim = 96
        net = openface.TorchNeuralNet(openfaceDir, imgDim)'''

    # merkel1Path = os.path.join(os.path.dirname(__file__), 'testImages', 'merkel.jpg')
    merkel1Path = "/home/sarah/Documents/dev/face_reg_root/images/chad_smith_2.jpeg"
    merkel2Path = os.path.join(os.path.dirname(__file__), 'testImages', 'ronaldo.jpg')
    # merkel2Path ="/home/sarah/Documents/dev/face_reg_root/images/sarah_face.jpg"

    img = cv2.imread(merkel1Path)
    img2 = cv2.imread(merkel2Path)
    # imgbox = make_rectangle(img)
    # cv2.imshow('rectangle', imgbox)
    # cv2.imshow('ImWin', img)
    # cv2.waitKey()

    box = get_boxes(img)
    alignedFace = aligner(box[0], img)

    box2 = get_boxes(img2)
    alignedFace2 = aligner(box2[0], img2)

    result = authorize_user([alignedFace], alignedFace2)
    print(f'result: {result}')

    rep = getRep(alignedFace)
    rep2 = getRep(alignedFace2)

    dist = get_euclidian_distance(rep, rep2)
    print(f"dist: {dist}")

    simil = get_cosine_similarity(rep, rep2)
    print(f'cosine similarity: {simil}')
