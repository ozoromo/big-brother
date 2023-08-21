from moviepy.video.io.VideoFileClip import VideoFileClip
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch
from faster_whisper import WhisperModel

from qa_algo_core import HelperFN, SpeechRecog, QAAlgo


model_name = "timpal0l/mdeberta-v3-base-squad2"  # set up hugging face model name

input_mp4_file = "audio.mp4"

wav_file_name = "audio.wav"  # location and name of converted audio file
audio_wav = HelperFN.extract_audio_from_mp4(input_mp4_file, wav_file_name)

recog = SpeechRecog("audio.wav")  # set the audio file which will be transcribed

context, tags = recog.transcribe()

question = "Was sind die grundlegenden Mechanismen, die in Prolog angewendet werden?"  # ask your question


qa_result = QAAlgo(model_name)
answer = qa_result.answer_question(context, question)

matching_segments = HelperFN.find_matching_segments(tags, answer)
merged_segments = HelperFN.merge_overlapping_segments(matching_segments)

print("\nQuestion:", question)
print("\nAnswer:", answer)
print("\nTime in seconds:", merged_segments)
