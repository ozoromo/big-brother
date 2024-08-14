import json
import base64
import gridfs
from bson import ObjectId

from pymongo import MongoClient
import nltk
from nltk.corpus import stopwords
from langdetect import detect

from sentence_transformers import SentenceTransformer

def preprocess_text(text):
    """
    Processes the input text by detecting its language, removing stop words, and tokenizing.

    Arguments:
    text -- string, the text to be processed.

    Returns:
    processed_text -- string, the processed text with stop words removed.
    """
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
    """
    Converts the input query into an embedding vector using a pre-trained model.

    Arguments:
    query -- string, the query to be embedded.

    Returns:
    embedding -- list, the embedding vector of the query.
    """
    embed_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    query = preprocess_text(query)
    embedding = embed_model.encode(query).tolist()

    return embedding

def find_similar_embeddings(embedding, collection):
    """
    Finds similar embeddings in the database collection using the provided embedding vector.

    Arguments:
    embedding -- list, the embedding vector to search for.
    collection -- MongoDB collection object where the embeddings are stored.

    Returns:
    found_videos -- list of dictionaries, each containing details of a found video with similar embeddings.
    """
    results = collection.aggregate([
        {"$vectorSearch": {
            "queryVector":embedding,
            "path": "embedding",
            "numCandidates": 500,
            "limit": 10,
            "index": "vector_index", 
            }
        },
        {
        "$project": {
            "_id": 0,
            "institute_name": 1,
            "course_name": 1,
            "video_id": 1,
            "segment_number": 1,
            "video_skript": 1,
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
        institute = videos['institute_name']
        score = videos['score']
        content = videos['video_skript']
        thumbnail_id = videos['thumbnail_id']
        video = {"institute": institute, "course": name, "video_id": id, "segment": segment, "thumbnail_id": thumbnail_id,
                  "video_script": content, "score": score}
        
        found_videos.append(video)
        print(f'Course: {name}, Segment {segment} of Video: {id} with score: {score}')

    return found_videos


def search(query, collection, db, collection_name):
    """
    Searches for similar videos in the collection based on the query, then filters it with a threshold.

    Arguments:
    query -- string, the query to search for.
    collection -- MongoDB collection object where the embeddings are stored.
    db -- MongoDB database object.
    collection_name -- string, the name of the collection containing video thumbnails.

    Returns:
    controlled_videos -- list of dictionaries, each containing details of videos with scores above a threshold.
    """
    query = preprocess_text(query)
    embedding = embed_query(query)

    videos = find_similar_embeddings(embedding, collection)
    videos_with_thumbnails = fetch_thumbnails(videos, db, collection_name)
    controlled_videos = []
    for video in videos_with_thumbnails:
        if video['score'] > 0.60:
            controlled_videos.append(video)
    return controlled_videos


def fetch_thumbnails(videos, db, collection_name):
    """
    Fetches and embeds thumbnails for the given videos from the GridFS collection.

    Arguments:
    videos -- list of dictionaries, each containing video details including thumbnail IDs.
    db -- MongoDB database object.
    collection_name -- string, the name of the GridFS collection for thumbnails.

    Returns:
    videos -- list of dictionaries, each containing video details with embedded thumbnail images.
    """
    fs = gridfs.GridFS(db, collection=collection_name)
    
    for video in videos:
        if 'thumbnail_id' in video:
            thumbnail_id = video['thumbnail_id']
            if isinstance(thumbnail_id, str):
                thumbnail_id = ObjectId(thumbnail_id)
            thumbnail_data = fs.get(thumbnail_id).read()

            thumbnail_base64 = base64.b64encode(thumbnail_data).decode('utf-8')
            video['thumbnail'] = f"data:image/jpeg;base64,{thumbnail_base64}"

    return videos