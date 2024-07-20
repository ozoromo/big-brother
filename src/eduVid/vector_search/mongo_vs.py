import os
import sys
import json

from pymongo import MongoClient
import nltk
from nltk.corpus import stopwords
from langdetect import detect

from sentence_transformers import SentenceTransformer

# Preprocessing function as defined above
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

def embed_query(query):
    embed_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    query = preprocess_text(query)
    embedding = embed_model.encode(query).tolist()

    return embedding

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

def find_similar_embeddings(embedding, collection):
    results = collection.aggregate([
        {"$vectorSearch": {
            "queryVector":embedding,
            "path": "embedding",
            "numCandidates": 400,
            "limit": 10,
            "index": "vector_index", 
            }
        },
        {
        "$project": {
            "_id": 0,
            "course_name": 1,
            "video_id": 1,
            "segment_number": 1,
            "thumbnail_id": 1,
            "score": { 
                "$meta": "vectorSearchScore" 
                }
            }
        }
    ])

    found_videos = []

    for videos in results:
        name = videos['course_name']
        id = videos['video_id']
        segment = videos['segment_number']
        score = videos['score']
        thumbnail_id = videos['thumbnail_id']
        video = {"course": name, "video_id": id, "segment": segment, "thumbnail_id": thumbnail_id, "score": score}
        found_videos.append(video)
        print(f'Course: {name}, Segment {segment} of Video: {id} with score: {score}')

    return found_videos

def search(query, collection):
    query = preprocess_text(query)
    embedding = embed_query(query)

    videos = find_similar_embeddings(embedding, collection)
    return videos

def vector_search(query):
    config_data = json.load(open("../config.json"))
    mongodb_uri = config_data['MONGO_URI']

    database_name = "BigBrother"
    collection_name = "extracted_data"
    
    client = MongoClient(mongodb_uri)
    collection = client[database_name][collection_name]

    return search(query, collection)
