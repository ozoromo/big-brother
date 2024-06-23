import cv2
from pytesseract import pytesseract
import numpy as np

from segment import Segment

# Class to gather data from Slide with Segmentierung
class SegmentOCR():
    def __init__(self, tesseract_path, images_folder, slide_separator='=== SLIDE ===', language='deu'):
        self.tesseract_path = tesseract_path
        self.images_folder = images_folder
        self.slide_separator = slide_separator
        self.language = language
        pytesseract.tesseract_cmd = self.tesseract_path
    
    def canny_edge_detection(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(gray_image, 100, 200)

        return edges
    
    def segment_detection(self, edges):

        # Adaptive Schwellenwertbildung
        adaptive_thresh = cv2.adaptiveThreshold(edges, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        # Morphologische Operationen zur Verbesserung der Segmentierung
        kernel = np.ones((5,5), np.uint8)
        morph = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(morph, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        segments = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w * h > 6000:
                segments.append(Segment(x,y,w,h))

        return segments

    def hierarchical_edge_detection(self, input_image_path):
        # Read the input image
        image = cv2.imread(input_image_path)
        img_height, img_width, _ = image.shape
    
        # Apply Canny edge detection
        canny_edges = self.canny_edge_detection(image)

        # Find the Segments
        segments = self.segment_detection(edges=canny_edges)

        # Create a hierarchical segment tree
        root = Segment(0, 0, img_width, img_height)
        root = root.create_segment_tree(segments, root)
        
        # Sort the tree
        root.sort_children()

        # OCR hierarchical tree
        root.ocr_segments(image)
        return root.text
