import cv2
from PIL import Image
from pytesseract import pytesseract
import os

class SlideOCR:
    """
    This class performs Optical Character Recognition (OCR) on 
    each extracted slide using Tesseract OCR. Tesseract is a popular OCR 
    engine. The recognized text from each slide is saved in an output text file.

    Usage:
    ```python
    # execute OCR
    slide_ocr_ = SlideOCR(tesseract_path, slides_folder, ocr_file)
    slide_ocr_.ocr_text_from_slides()
    ```
    """
    def __init__(self, tesseract_path, images_folder, output_file, slide_separator='=== SLIDE ===', language='deu'):
        self.tesseract_path = tesseract_path
        self.images_folder = images_folder
        self.output_file = output_file
        self.slide_separator = slide_separator
        self.language = language

    def ocr_text_from_slides(self):
        # Set Tesseract OCR executable path
        pytesseract.tesseract_cmd = self.tesseract_path

        # Get the file names in the directory
        file_texts = []

        for root, dirs, file_names in os.walk(self.images_folder):
            # Iterate over each file name in the folder
            for file_name in file_names:
                # Construct the full path to the image file
                image_path = os.path.join(root, file_name)

                # Read the image using OpenCV
                img = cv2.imread(image_path, 0)  # Read as grayscale

                # Apply thresholding to the image
                _, thresholded_img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

                # Create a PIL Image object from the thresholded image
                pil_img = Image.fromarray(thresholded_img)

                # Extract text from the thresholded image with the specified language
                text = pytesseract.image_to_string(pil_img, lang=self.language)

                # Append the extracted text to the list
                file_texts.append(text)

        # Join the file texts using the slide separator
        merged_text = '\n\n'.join([f"{self.slide_separator}\n{text}" for text in file_texts])

        # Save the merged output as a single text file
        with open(self.output_file, 'w', encoding='utf-8') as file:
            file.write(merged_text)
