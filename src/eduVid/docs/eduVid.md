## Slide Extraction - extract_slides_from_video()
### Description:
This method extracts individual slides from the input video. It utilizes the `slides_extractor` module to perform the extraction and saves each slide as an image file in the specified `slides_folder`.
### Parameters:
- `video_path` (string): The path to the input video file (in mp4 format).
- `slides_folder`(string): The path to directory where extracted slides will be saved.
### Usage:
```python
# execute Slide extractor
slide_extractor_ = SlideExtractor(video_path, slides_folder)
slide_extractor_.extract_slides_from_video()
```
---
## OCR (Optical Character Recognition) - ocr_text_from_slides()
### Description:

This method performs Optical Character Recognition (OCR) on each extracted slide using Tesseract OCR. Tesseract is a popular OCR engine. The recognized text from each slide is saved in an output text file.
### Parameters:
- `video_path` (string): The path to the input video file (in mp4 format).
- `slides_folder`(string): The path to directory where slides will taken from.
### Usage:
```python
# execute OCR
slide_ocr_ = SlideOCR(tesseract_path, slides_folder, ocr_file)
slide_ocr_.ocr_text_from_slides()
```
---
