import os
import sys
import json
import requests
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "handle_presentation"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "question_answering"))
from slides_extractor import SlideExtractor
from slides_ocr import SlideOCR
from qa_algo_core import HelperFN,SpeechRecog

from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader
from sentence_transformers import SentenceTransformer

from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
from threading import Lock

from nltk.corpus import stopwords
from langdetect import detect
import nltk

from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId
from moviepy.video.io.VideoFileClip import VideoFileClip


# Global variables for slide counting and slide limit
# Because LLama Parse allows only 1000 free page parsing daily...
slide_counter = Counter()
slide_counter_lock = Lock()
slide_limit_reached = False
# Global list to store processed video IDs
processed_video_ids = []

# Run this locally with venv

# Load processed video IDs
def load_processed_video_ids():
    try:
        with open("processed_video_ids.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save processed video IDs
def save_processed_video_ids(video_ids):
    with open("processed_video_ids.json", "w") as f:
        json.dump(video_ids, f)

# Merge non-sentence tags
def merge_clusters(data):
    merged_tags = []
    current_start = data['tags'][0][0]
    current_end = data['tags'][0][1]
    current_text = data['tags'][0][2]

    # Merge not ending sentences
    for i in range(1, len(data['tags'])):
        start, end, text = data['tags'][i]
        
        if not current_text.endswith('.'):
            current_end = end
            current_text += text
        else:
            merged_tags.append([current_start, current_end, current_text])
            current_start = start
            current_end = end
            current_text = text

    # Append the last cluster
    merged_tags.append([current_start, current_end, current_text])
    
    # Update the data
    data['tags'] = merged_tags
    return data

# Preprocess the text before encoding
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

# Load JSON file containing course IDs and names
def load_course_data(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        course_data = json.load(f)
    return course_data

# Find course name and institute name by course ID
def find_course_and_institute(course_data, course_id):
    for institute in course_data:
        institute_name = institute["name"]
        for course in institute["courses"]:
            if course["course_id"] == course_id:
                return course["course_name"], institute_name
    return None, None

# Download the video
def download_video(fs, video_id, save_path):
    # Ensure directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    grid_out = fs.get(video_id)

    with open(save_path, 'wb') as video_file:
        video_file.write(grid_out.read())
    return save_path

# Mp4 Video -> Mp3 Wav *-> Txt Text *[s2t Algorithm]
def extract_audio_and_script(video_file, start_time, end_time):
    audio_file = video_file.replace('.mp4', f'_segment_{start_time}_{end_time}.wav')
    print("Started extraction of audio...")
    helper = HelperFN()
    helper.extract_audio_from_mp4_segment(video_file, audio_file, start_time, end_time)
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
    global slide_counter, slide_limit_reached
    slides_dir = video_file.replace('.mp4', f'_slides_segment_{segment_number}')
    print("Started extraction of slides...")
    extractor = SlideExtractor(video_file, slides_dir, start_time, end_time)
    extractor.extract_slides_from_video()
    print("Slide extraction completed.")

    print("Started slide parsing...")
    documents = SimpleDirectoryReader(input_dir=slides_dir, file_extractor=file_extractor).load_data()
    slides_info = []

    with slide_counter_lock:
        if slide_counter['count'] + len(documents) > 900:
            print("Slide limit of 900 reached. Stopping until tomorrow...")
            slide_limit_reached = True

        slide_counter['count'] += len(documents)

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

# Extract data from the whole video, divide the video into 10 minute-segments
def extract_data_from_video(video_dir, institute_name, course_name, course_id, parser, embed_model):
    global processed_video_ids
    def process_segment(start_time, end_time, segment_number):
        with ThreadPoolExecutor() as executor:
            future_script = executor.submit(extract_audio_and_script, video_file, start_time, end_time)
            future_slides = executor.submit(extract_and_parse_slides, video_file, start_time, end_time, segment_number, file_extractor)

            context, tags = future_script.result()
            slides_info = future_slides.result()

        segment_data = {
            "institute_name": institute_name,
            "course_id": course_id,
            "course_name": course_name,
            "video_id": video_id,
            "segment_number": segment_number,
            "video_skript": context,
            "tags": tags,
            "slides": slides_info
        }

        segment_data = merge_clusters(segment_data)

        # Text embedding
        print("Started text encoding for segment", segment_number)
        combined_text = segment_data['video_skript']
        combined_text += ' '.join(slide['text'] for slide in segment_data['slides'])
        preprocessed_text = preprocess_text(combined_text)

        segment_data['embedding'] = embed_model.encode(preprocessed_text).tolist()
        print("Text encoding completed for segment", segment_number)

        segment_data_path = os.path.join("./storage", f"{course_id}_{video_id}_segment_{segment_number}.json")

        with open(segment_data_path, 'w', encoding='utf-8') as f:
            json.dump(segment_data, f, ensure_ascii=False, indent=4)

        print(f"JSON data for segment {segment_number} created successfully.")
    
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

    # Save processed video IDs
    processed_video_ids.append(video_id)
    save_processed_video_ids(processed_video_ids)

# Process videos from mongodb
def process_videos_from_mongodb(uri, db_name, collection_name):
    global slide_limit_reached, processed_video_ids
    processed_video_ids = load_processed_video_ids()
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]
    fs = gridfs.GridFS(db)

    config_data = json.load(open("config.json"))
    LLAMA_TOKEN = config_data["LLAMA-CLOUD"]

    embed_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    parser = LlamaParse(api_key=LLAMA_TOKEN, result_type="text")

    for video_record in collection.find():
        if slide_limit_reached:
            print("Slide limit reached. Skipping video processing.")
            break
            
        video_id = video_record['video_id']
        course_id = video_record['course_id']

        course_data = load_course_data('course_ids.json')
        course_name, institute_name = find_course_and_institute(course_data, course_id)
        if course_name is None or institute_name is None:
            print(f"Course ID {course_id} not found in the JSON file.")
            continue

        # Check if video ID is already processed
        if video_id in processed_video_ids:
            print(f"Video {video_id} already processed. Skipping.")
            continue

        video_path = download_video(fs, video_id, f"./video_dir/{institute_name}/{course_id}/video_{video_id}.mp4")
        
        extract_data_from_video(video_path, institute_name, course_name, course_id, 
                                parser, embed_model)

# Upload the extracted json data to mongodb
def upload_extracted_data():
    return
    #TODO...



if __name__ == "__main__":
    config_data = json.load(open("config.json"))
    LLAMA_TOKEN = config_data["LLAMA-CLOUD"]
    mongo_uri = config_data["MONGO_URI"]

    database_name = "BigBrother"
    collection_name = ""

    process_videos_from_mongodb(mongo_uri, database_name, collection_name)

    