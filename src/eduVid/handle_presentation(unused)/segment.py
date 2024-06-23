from pytesseract import pytesseract 

class Segment:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.children = []
        self.text = ""
        self.language = 'deu'
        
    def __str__(self, level=0):
        ret = "\t"*level + f"[{self.x}, {self.y}, {self.w}, {self.h}]\n"
        for child in self.children:
            ret += child.__str__(level+1)
        return ret
    
    def sort_children(self):
        # Sort children by y, then by x
        self.children.sort(key=lambda child: (child.y, child.x))
        # Recursively sort each child's children
        for child in self.children:
            child.sort_children()
    
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
    
    def ocr_segments(self, image):
        if self.children == []:
            # Draw this segment
            x, y, w, h = self.x, self.y, self.w, self.h

            roi = image[y:y+h, x:x+w]

            # Use Tesseract to do OCR on the ROI
            self.text = pytesseract.image_to_string(roi, lang=self.language)
            print("Found String:", self.text)
        else:
            child_text = ""
            for node in self.children:
                node.ocr_segments(image)
                child_text = child_text + node.text
            
            for teilsting in child_text.split():
                if teilsting in self.text:
                    self.text.replace(teilsting, "")
            self.text = self.text + child_text + "\n"
        return