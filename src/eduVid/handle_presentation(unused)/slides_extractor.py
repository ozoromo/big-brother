import cv2
import os
import shutil
import numpy as np

class SlideExtractor:
    def __init__(self, video_path: str, output_folder: str, threshold: int = 20.0):
        """
        Arguments:
        video_path --  The path to the input video file (in mp4 format).
        slides_folder -- The path to directory where extracted slides will be saved.
        """
        self.video_path = video_path
        self.output_folder = output_folder
        self.threshold = threshold

    def save_slide(self, previous_frame, time_from, timestamp, slide_counter):

        print(f"Slide {slide_counter} change detected at timestamp: {timestamp:.1f} seconds")
        slide_filename = os.path.join(self.output_folder, f"slide_[{time_from}-{timestamp:.1f}].jpg")
        cv2.imwrite(slide_filename, previous_frame)

    def extract_slides_from_video(self):
        """
        This method extracts individual slides from the input video.
        It utilizes the `slides_extractor` module to perform the extraction and
        saves each slide as an image file in the specified `slides_folder`.

        Usage:
        ```
        slide_extractor_ = SlideExtractor(video_path, slides_folder)
        slide_extractor_.extract_slides_from_video()
        ```
        """
        # Create the output folder if it doesn't exist
        os.makedirs(self.output_folder, exist_ok=True)

        # Empty the slides folder if it exists
        if os.path.exists(self.output_folder):
            shutil.rmtree(self.output_folder)
            os.makedirs(self.output_folder)

        # Load the video
        video = cv2.VideoCapture(self.video_path)
        if not video.isOpened():
            print("Error opening video file.")
            return

        # Initialize variables
        slide_counter = 0
        frame_counter = 0
        time_from = 0
        previous_frame = None
        colored_frame = None

        fps = video.get(cv2.CAP_PROP_FPS)

        # Process video frames
        while True:
            # Read the next frame
            end, frame = video.read()
            if not end:
                break

            # Convert frame to grayscale for simplicity
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Check for a change in the slide
            if previous_frame is not None:

                frame_diff = cv2.absdiff(gray, previous_frame)
                difference_score = frame_diff.mean()
            
                if difference_score > self.threshold:
                    # If a slide change is detected, save the previous slide as a JPG image
                    self.save_slide(colored_frame, time_from, (frame_counter/fps), slide_counter)
                    slide_counter += 1
                    time_from = frame_counter/fps

            # Update the previous frame with the current frame for the next iteration
            previous_frame = gray
            colored_frame = frame
            frame_counter += 1

        # Save the last slide
        slide_counter += 1
        print(f"Slide {slide_counter} change detected at timestamp: {frame_counter/fps:.1f} seconds")
        slide_filename = os.path.join(self.output_folder, f"slide_[{time_from:.1f}-{frame_counter/fps:.1f}].jpg")
        cv2.imwrite(slide_filename, previous_frame)

        # Release the video capture
        video.release()
