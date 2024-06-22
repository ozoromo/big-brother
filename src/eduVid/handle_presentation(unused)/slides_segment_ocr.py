import cv2
from pytesseract import pytesseract 
from pytesseract import Output
from PIL import Image
import numpy as np
import os

class Segment:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.children = []

# Class to gather data from Slide with Segmentierung
class SegmentOCR():
    def __init__(self, tesseract_path, images_folder, slide_separator='=== SLIDE ===', language='deu'):
        self.tesseract_path = tesseract_path
        self.images_folder = images_folder
        self.slide_separator = slide_separator
        self.language = language
        self.color = [(128, 0, 128), (0, 0, 255), (173, 216, 230), (0, 255, 255), (0, 128, 0), (255, 165, 0), (255, 0, 0), (255, 0, 127), (255, 0, 255)]
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
            if w * h > 1000:
                segments.append(Segment(x,y,w,h))

        return segments
    
    def sort_segments(self, segments):
        # Sort rectangles by x-coordinate (left to right)
        sorted_segments = sorted(segments, key=lambda rect: rect.x)
        return sorted_segments
    
    def create_segment_tree(self, segments, root):
        sorted_segments = self.sort_segments(segments)
        # Root is always the biggest square that contains all segments - root will never change
        for segm in sorted_segments[1:]:
            self.insert_into_tree(root, segm)
        return root
    
    def insert_into_tree(self, parent, child):
        for node in parent.children:
            # This child is a grandchild, recursive call
            # parent > node > child
            if self.is_contained(node, child):
                self.insert_into_tree(node, child)
                return  # child inserted as a descendant
            
            # This child actually bigger than parent's child, recursive call  
            # parent > child > node
            elif self.is_contained(child, node):
                parent.children.remove(node)
                child.children.append(node)
                parent.children.append(child)
                return # child inserted as a children
            
        # This child is actually parent's child
        # parent > {node, child}
        parent.children.append(child)

    
    def is_contained(self, parent_rect, child_rect):
        # Check if child rectangle is completely contained within parent rectangle
        return (parent_rect.x <= child_rect.x and
                parent_rect.y <= child_rect.y and
                parent_rect.x + parent_rect.w >= child_rect.x + child_rect.w and
                parent_rect.y + parent_rect.h >= child_rect.y + child_rect.h)
    
    def draw_segments(self, segment, image, depth):
        # Draw this segment
        x, y, w, h = segment.x, segment.y, segment.w, segment.h
        color = self.color[depth] if depth <= len(self.color) else self.color[-1]
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        # Draw each child 
        for child in segment.children:
            image = self.draw_segments(child, image, depth+1)
        return image
    
    def ocr_segments(self, segment, image):
        x, y, w, h = segment.x, segment.y, segment.w, segment.h
        rio = image[y:y+h, x:x+w]
        segment.text = pytesseract.image_to_string(rio)
        

    def segment_detection_test(self, edges):

        # Adaptive Schwellenwertbildung
        adaptive_thresh = cv2.adaptiveThreshold(edges, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        # Morphologische Operationen zur Verbesserung der Segmentierung
        kernel = np.ones((5,5), np.uint8)
        morph = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(morph, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        segments = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w * h > 1000:
                segments.append(Segment(x,y,w,h))

        return segments


    def hierarchical_edge_detection(self, input_image_path):
        # Read the input image
        image = cv2.imread(input_image_path)
        img_height, img_width, _ = image.shape
    
        # Apply Canny edge detection
        canny_edges = self.canny_edge_detection(image)
        
        canny_output = np.zeros_like(image)
        canny_output[canny_edges != 0] = [255, 255, 255]

        segments = self.segment_detection_test(edges=canny_edges)
        root = self.create_segment_tree(segments, Segment(0, 0, img_width, img_height))

        # TODO: Efficient way to extract texts from sorted tree of segments
