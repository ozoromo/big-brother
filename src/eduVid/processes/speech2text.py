# Importiere die Module
import moviepy.editor as mp
import os

class VideoScript:
    def __init__(self, model):
        self.model = model

    def transcribe_video(self, video_path, output_dir):

        video = mp.VideoFileClip(video_path)
        audio = video.audio

        os.makedirs(output_dir, exist_ok=True)

        audio_file_path = os.path.join(output_dir, "audio.wav")
        audio.write_audiofile(audio_file_path)

        video.close()

        result = self.model.transcribe(audio_file_path)

        transcript_file_path = os.path.join(output_dir, "transcript.txt")
        with open(transcript_file_path, "w") as f:
            f.write(result["text"])

        transcript_form_file_path = os.path.join(output_dir, "transcript_form.txt")
        with open(transcript_form_file_path, "w") as f:
            sentences = result["text"].split(".")
            for sentence in sentences:
                sentence = sentence + "."
                f.write(sentence + "\n")
