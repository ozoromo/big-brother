import os
import sys
import json
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "handle_presentation"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "question_answering"))
from slides_extractor import SlideExtractor
from slides_ocr import SlideOCR
from qa_algo_core import HelperFN,SpeechRecog

def extract_data_from_video(video_dir):
    video_file = os.path.join(video_dir, f"{os.path.basename(video_dir)}.mp4")
    slides_dir = os.path.join(video_dir, "slides")
    # multiprocessing to fasten?
    # Mp4 Video -> Mp3 Wav *-> Txt Text *[s2t Algorithm]
    audio_file = video_file.replace('.mp4', '.wav')
    helper = HelperFN()
    helper.extract_audio_from_mp4(video_file, audio_file)
    recog = SpeechRecog(audio_file)
    context, tags = recog.transcribe()

    # Mp4 Video -> Png Slide
    extractor = SlideExtractor(video_file, slides_dir)
    extractor.extract_slides_from_video()

    # Png Slide -> Txt Slide [SlideOCR]
    # TODO: More accurate OCR of Slides -> Do not save txt, return the String.
    slide_ocr = SlideOCR()
    slide_text = slide_ocr.ocr_text_from_slides()

    video_data = {
        "video_file": video_file,
        "video_skript": context,
        "tags": tags,
        "slide_context": slide_text
    }

    video_data_path = os.path.join(video_dir, "data.json")
    with open(video_data_path, 'w', encoding='utf-8') as f:
        json.dump(video_data, f, ensure_ascii=False, indent=4)



def extract_data_from_all_videos():
    DOWNLOAD_PATH = "./video_dir"
    TESSERACT_PATH = '/opt/homebrew/bin/tesseract' # Change this to your tesseract path

    with open('course_ids.json', 'r', encoding='utf-8') as f:
            courses_data = json.load(f)

    all_course_ids = []
    all_institut_names = []

    for institute in courses_data:
        for course in institute['courses']:
            all_course_ids.append(course['course_id'])
            all_institut_names.append(institute['name'])

    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)

    for i, course_id in enumerate(all_course_ids):

        institut_dir = os.path.join(DOWNLOAD_PATH, all_institut_names[i])
        course_dir = os.path.join(institut_dir, course_id)

        video_dirs = [os.path.join(course_dir, f) for f in os.listdir(course_dir) if os.path.isdir(os.path.join(course_dir, f))]

        for video_dir in video_dirs:
            extract_data_from_video(video_dir)
