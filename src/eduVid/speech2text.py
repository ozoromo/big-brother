# Importieren der benötigten Module
from pvrecorder import PvRecorder
import wave, struct 
import whisper
import moviepy.editor as mp
import requests
import os

# Laden des Whisper-Modells. Wir können "tiny = 32x Geschwindigkeit" ausprobieren; base und medium sind besser, aber langsamer
tiny = whisper.load_model("tiny")
fp16=False

# Angeben der URL zur Videodatei
video_url = 'https://video.isis.tu-berlin.de/isisvideo/file?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6ImV4dCJ9.eyJ0eXBlIjoidmlkZW8iLCJoYXNoIjoiZGEyODk3M2U1YzFkNGM2MzYyOWNjMDI5NmYzNDM0MDFhZGQ3YzI0NWZkN2QwNzU1ZWIyNzUzNWQ4YjVkM2NmZiIsImZpbGVfZXh0IjoiLm1wNCIsImlzcyI6ImV4dCIsInJvbGUiOjAsInJpZCI6Ijg3LjEzNS4xNzYuMTIzIiwiZXhwIjoxNjg1NjY0MDAwfQ.baSnFQWvNmgX2dz1SvsUQcpOp3Ovs2joPtRRKdgswRM'
audio_path = 'audio_from_video.wav'

# Herunterladen der Videodatei an einen temporären Ort
temp_path = 'temp_video.mp4'
r = requests.get(video_url)
with open(temp_path, 'wb') as f:
    f.write(r.content)

# Extrahieren des Audios aus dem Video
video_clip = mp.VideoFileClip(temp_path)
audio_clip = video_clip.audio
audio_clip.write_audiofile(audio_path)

# Transkribieren des Audios mit dem Whisper-Modell
result=tiny.transcribe(audio_path)
print(result["text"]) 

# Löschen der temporären Videodatei
os.remove(temp_path)