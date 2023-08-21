###############################################
#         Make THIS script executable         #
###############################################
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "eduVid", "question_answering"))

###############################################
#       The actual program starts here        #
###############################################
from qa_algo_core import HelperFN, SpeechRecog, QAAlgo

# set up hugging face model name
model_name = "timpal0l/mdeberta-v3-base-squad2"

input_mp4_file = "audio.mp4"
wav_file_name = "audio.wav"

audio_wav = HelperFN.extract_audio_from_mp4(input_mp4_file, wav_file_name)

recog = SpeechRecog(wav_file_name)  # set the audio file which will be transcribed
context, tags = recog.transcribe()
question = "Was sind die grundlegenden Mechanismen, die in Prolog angewendet werden?"

qa_result = QAAlgo(model_name)
answer = qa_result.answer_question(context, question)
matching_segments = HelperFN.find_matching_segments(tags, answer)
# Returns a list with time intervals at which the answer might be
merged_segments = HelperFN.merge_overlapping_segments(matching_segments)

print("\nQuestion:", question)
print("\nAnswer:", answer)
print("\nTime in seconds:", merged_segments)
