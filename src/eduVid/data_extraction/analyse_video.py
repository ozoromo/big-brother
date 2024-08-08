import os
import sys
import json
import shutil

from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader
from sentence_transformers import SentenceTransformer

from concurrent.futures import ThreadPoolExecutor
from nltk.corpus import stopwords
from langdetect import detect
import nltk

from moviepy.video.io.VideoFileClip import VideoFileClip
import cv2
from pymongo import MongoClient
import gridfs

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "handle_presentation"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "question_answering"))

from slides_extractor import SlideExtractor
from qa_algo_core import HelperFN, SpeechRecog

def preprocess_text(text):
    # Detect language
    try:
        language = detect(text)
    except:
        language = 'unknown'

    if language == 'de':
        stop_words = set(stopwords.words('german'))
    elif language == 'en':
        stop_words = set(stopwords.words('english'))
    else:
        stop_words = set(stopwords.words('english')) | set(stopwords.words('german'))

    words = nltk.word_tokenize(text)
    processed_words = []
    for word in words:
        if word not in stop_words:
            processed_words.append(word)
    processed_text = ' '.join(processed_words)
    return processed_text

# Mp4 Video -> Mp3 Wav *-> Txt Text *[s2t Algorithm]
def extract_audio_and_script(video_file, start_time, end_time):
    audio_file = video_file.replace('.mp4', f'_segment_{start_time}_{end_time}.wav')
    print("Started extraction of audio...")
    helper = HelperFN()
    helper.extract_audio_from_mp4(video_file, audio_file, start_time, end_time)
    print("Audio extraction completed.")

    print("Started extraction of script...")
    recog = SpeechRecog(audio_file)
    context, tags = recog.transcribe()
    print("Script extraction completed.")

    for i, tag in enumerate(tags):
        tag[0] = round(tag[0], 1)
        tag[1] = round(tag[1], 1)
        tags[i] = tag
    
    # Delete audio file after transcription
    os.remove(audio_file)
    print(f"Deleted audio file: {audio_file}")

    return context, tags

# Mp4 Video -> Png Slide
def extract_and_parse_slides(video_file, start_time, end_time, segment_number, file_extractor):

    slides_dir = video_file.replace('.mp4', f'_slides_segment_{segment_number}')
    print("Started extraction of slides...")
    extractor = SlideExtractor(video_file, slides_dir, start_time, end_time)
    extractor.extract_slides_from_video()
    print("Slide extraction completed.")

    print("Started slide parsing...")

    slides_info = []
    timeout_seconds = 2 * 60  # 2 minutes

    def load_data_with_timeout():
        documents = SimpleDirectoryReader(input_dir=slides_dir, file_extractor=file_extractor, raise_on_error=True).load_data()
        return documents
    with ThreadPoolExecutor() as executor:
        future = executor.submit(load_data_with_timeout)
        try:
            documents = future.result(timeout=timeout_seconds)
        except TimeoutError:
            print("Slide parsing timed out. Skipping this segment.")
            shutil.rmtree(slides_dir)
            return slides_info  # Return empty slides info if timeout occurs
        except Exception as e:
            print(f"An error occurred while parsing slides: {e}")
            shutil.rmtree(slides_dir)
            return slides_info  # Return empty slides info if an error occurs


    for doc in documents:
        slide_info = {
            "file_name": doc.metadata['file_name'],
            "text": doc.text.strip()
        }
        slides_info.append(slide_info)
    print("Slide parsing completed.")

    # Delete slides directory after parsing
    shutil.rmtree(slides_dir)
    print(f"Deleted slides directory: {slides_dir}")

    return slides_info

# Extract thumbnail
def extract_thumbnail(video_file, start_time, uri, thumbnail_size = (640, 480)):
    db_name = "BigBrother"
    collection_name = "thumbnails"
    client = MongoClient(uri)
    db = client[db_name]

    capture_time = start_time + 1 
    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        print("Error opening video file.")
        return None

    cap.set(cv2.CAP_PROP_POS_MSEC, capture_time * 1000)
    ret, frame = cap.read()
    cap.release()

    if ret:
        # Resize the frame to the desired thumbnail size
        resized_frame = cv2.resize(frame, thumbnail_size)
        # Convert frame to JPEG image in memory
        _, buffer = cv2.imencode('.jpg', resized_frame)
        # Store JPEG buffer in MongoDB using GridFS
        fs = gridfs.GridFS(db, collection=collection_name)
        thumbnail_id = fs.put(buffer.tobytes())
        print("Thumbnail saved successfully as blob.")
        return thumbnail_id
    else:
        print(f"Error capturing thumbnail at time {capture_time} seconds.")
        return None

# Upload the extracted json data to mongodb
def upload_extracted_data(json_data, uri):

    db_name = "BigBrother"
    collection_name = "extracted_data"
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    json_str = json.dumps(json_data)
    data = json.loads(json_str)

    collection.insert_one(data)

def extract_data_from_video(video_dir, institute_name, course_name, course_id, parser, embed_model):

    if len(os.listdir(video_dir)) < 1:
        print("This video is already analysed.")
        return
    config_data = json.load(open("../config.json"))
    uri = config_data["MONGO_URI2"]

    def process_segment(start_time, end_time, segment_number):
        with ThreadPoolExecutor() as executor:
            future_script = executor.submit(extract_audio_and_script, video_file, start_time, end_time)
            future_slides = executor.submit(extract_and_parse_slides, video_file, start_time, end_time, segment_number, file_extractor)

            context, _ = future_script.result()
            slides_info = future_slides.result()

        thumbnail_id = extract_thumbnail(video_file, start_time, uri)
        
        segment_data = {
            "institute_name": institute_name,
            "course_id": course_id,
            "course_name": course_name,
            "video_id": video_id,
            "segment_number": segment_number,
            "thumbnail_id": str(thumbnail_id),
            "video_skript": context,
            "slides": slides_info,
        }

        # Text embedding
        print("Started text encoding for segment", segment_number)
        combined_text = segment_data['video_skript']
        combined_text += ' '.join(slide['text'] for slide in segment_data['slides'])
        preprocessed_text = preprocess_text(combined_text)

        segment_data['embedding'] = embed_model.encode(preprocessed_text).tolist()
        print("Text encoding completed for segment", segment_number)

        upload_extracted_data(segment_data, uri)

        print(f"JSON data for segment {segment_number} uploaded successfully.")
    
    file_extractor = {".jpg": parser}
    video_id = int((os.path.basename(video_dir)).replace("video_", ""))
    video_file = os.path.join(video_dir, f"{os.path.basename(video_dir)}.mp4")

    # Determine the duration of the video
    with VideoFileClip(video_file) as video:
        duration = video.duration

    segment_duration = 10 * 60  # 10 minutes in seconds
    num_segments = int(duration // segment_duration) + 1

    for segment_number in range(1, num_segments + 1):
        start_time = (segment_number - 1) * segment_duration
        end_time = min(segment_number * segment_duration, duration)
        process_segment(start_time, end_time, segment_number)

    # Delete video file after processing
    os.remove(video_file)
    print(f"Deleted video file: {video_file}")


def extract_data_from_all_videos(dowload_path, LLAMA_TOKEN):


    embed_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    parser = LlamaParse(api_key=LLAMA_TOKEN, result_type="text")

    with open('../scrapers/video_scraper/course_ids_selbst.json', 'r', encoding='utf-8') as f:
        courses_data = json.load(f)

    all_course_ids = []
    all_course_names = []
    all_institut_names = []

    for institute in courses_data:
        for course in institute['courses']:
            all_course_ids.append(course['course_id'])
            all_course_names.append(course['course_name'])
            all_institut_names.append(institute['name'])

    for i, course_id in enumerate(all_course_ids):

        institut_dir = os.path.join(dowload_path, all_institut_names[i])
        course_dir = os.path.join(institut_dir, course_id)
        course_name = all_course_names[i]
        institute_name = all_institut_names[i]

        video_dirs = [os.path.join(course_dir, f) for f in os.listdir(course_dir) if os.path.isdir(os.path.join(course_dir, f))]


        for video_dir in video_dirs:
            print(f"Starting processing: {video_dir}")
            extract_data_from_video(video_dir, institute_name, course_name, course_id, parser, embed_model)
            print(f"Process finished {video_dir}!")


if __name__ == "__main__":
    DOWNLOAD_PATH = "../scrapers/video_scraper/video_dir"
    config_data = json.load(open("../config.json"))
    LLAMA_TOKEN = config_data["LLAMA-CLOUD"]

    extract_data_from_all_videos(DOWNLOAD_PATH, LLAMA_TOKEN)
