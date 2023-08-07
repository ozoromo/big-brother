# eduVid
---
## Structure:
```bash
/eduVid
├── /docs
├── /input
├── /output
├── /processes
│   ├── keyword_extractor.py
│   ├── slides_extractor.py
│   ├── slides_ocr.py
│   ├── speech2text.py
│   └── summarization.py
├── /zipf
├── VideoPlayer.py
├── main.py
└── requirements.txt
```
---
## Speech-to-Text (S2T) - transcribe_video(video_path, output_path)
### Description:
This method performs Speech-to-Text conversion on the input video using the `whisper` library. It utilizes a pre-trained neural network model to transcribe the speech from the video into text. The resulting transcript is saved in an output file.
### Parameters:
-   `video_path` (string): The path to the input video file (in mp4 format).
-   `output_path` (string): The path to the directory where the generated output files will be stored.
- `model`:  instance of the custom transcription model used for converting audio to text from whisper.
### Usage:
```python
# whisper settings
model = whisper.load_model("base")
fp16 = False

# execute S2T
transcriber = VideoScript(model)
transcriber.transcribe_video(video_path, output_path)
```
---
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
## Summarization - summarize_file(input_file, summary_file)
### Description:

This method generates a summary of the content present in the specified input text file. It uses a text summarization algorithm implemented in the `summarization` module to create the summary. The resulting summary is saved in the specified summary file.
### Parameters:

-   `input_file` (string): The path to the input text file that needs to be summarized.
-   `summary_file` (string): The path to the output file where the summary will be saved.
### Usage:
```python
# execute summarizer
summarizer = TextSummarizer()
summarizer.summarize_file(ocr_file, summary_file)
```
---
## Keyword Extraction - extract_keywords(input_file)
### Description:

This method extracts keywords from the content present in the specified input text file. It uses a keyword extraction algorithm implemented in the `keyword_extractor` module to identify important keywords. The extracted keywords are returned as a list.

### Parameters:

-   `input_file` (string): The path to the input text file from which keywords need to be extracted.
### Usage:
```python
# execute keyword extractor
keyword_extractor = KeywordExtractor()
extracted_keywords = keyword_extractor.extract_keywords(summary_file)
```
---
## Keyword Saving - save_keywords(keywords, keywords_file)

### Description:

This method saves the extracted keywords into a specified output file.

### Parameters:

-   `keywords` (list): The list of extracted keywords.
-   `keywords_file` (string): The path to the output file where the keywords will be saved.
### Usage:
```python
# save keywords
keyword_extractor.save_keywords(extracted_keywords, keywords_file)
```
---
## def wipe_folder(folder_path)

### Description:

This method is responsible for recursively wiping out all contents within a specified folder. It is used to clean the output folder before starting the data processing tasks.

### Parameters:

-   `folder_path` (string): The path to the folder that needs to be cleared.
### Usage:
```python
wipe_folder(output_path)
```
---
## def zip_output_files(main_directory, output_path, zip_path)

### Description:

This method creates a zip file containing all the generated output files. The output files are stored in the `output_path` directory, and the zip file is saved in the `zip_path` directory.

### Parameters:

-   `main_directory` (string): The main directory path where the script is located.
-   `output_path` (string): The path to the directory containing the generated output files.
-   `zip_path` (string): The path to the directory where the zip file should be saved.
### Usage:
```python
zip_output_files(main_directory, output_path, zip_path)
```
---
## VideoPlayer Class
based on `tkinter` module

### `__init__(self, video_path)`

Constructor method for the `VideoPlayer` class. Initializes the video player application and sets up the GUI components.

-   Parameters:
    -   `video_path` (str): The path to the video file to be played.

### `play(self)`

Plays the video using the VLC media player. Initializes the video media and sets the player window inside the frame. Also registers an event to handle the end of video playback.

### `toggle_playback(self)`

Toggles the video playback between play and pause. If the video is currently playing, it will be paused, and if it is paused, it will be resumed.

### `update_time_labels(self)`

Updates the time labels to display the current playback time and total duration of the video. It is called periodically to keep the time labels updated while the video is playing or paused.

### `format_time(self, milliseconds)`

Converts the given time in milliseconds to the format HH:MM:SS.

-   Parameters:
    
    -   `milliseconds` (int): Time in milliseconds to be formatted.
-   Returns:
    
    -   `formatted_time` (str): The formatted time in the format HH:MM:SS.

### `update_video(self, value)`

Updates the video playback position based on the value of the timeline scale. It is called when the user interacts with the timeline scale to seek the video to a specific position.

-   Parameters:
    -   `value` (float): The position value selected on the timeline scale (0 to 100).

### `handle_end_reached(self, event)`

Handles the event when the end of video playback is reached. It shows the replay button to allow the user to restart the video.

-   Parameters:
    -   `event`: The event object representing the end of video playback.

### `replay_video(self)`

Restarts the video playback from the beginning when the replay button is clicked. It hides the replay button after starting the video.

### `select_chapter(self, chapter_time)`

Allows the user to jump to a specific chapter in the video by selecting a chapter button. It sets the video playback position to the specified chapter time and starts playing from that position.

-   Parameters:
    -   `chapter_time` (int): The time in milliseconds where the selected chapter starts.

## Main (`__name__ == '__main__'`)

### `video_path`

The path to the video file that will be played in the video player. This variable should be updated with the correct path to the video file before running the application.

### `player = VideoPlayer(video_path)`

Creates an instance of the `VideoPlayer` class and starts the video player application with the specified video file. The video player GUI will be displayed, and the user can interact with the controls to play, pause, seek, and jump to chapters in the video.
