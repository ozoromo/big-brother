import cv2
import os
import shutil

class SlideExtractor:
    def __init__(self, video_path: str, output_folder: str):
        """
        Arguments:
        video_path --  The path to the input video file (in mp4 format).
        slides_folder -- The path to directory where extracted slides will be saved.
        """
        self.video_path = video_path
        self.output_folder = output_folder

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
        frame_counter = 0
        slide_counter = 0
        previous_frame = None

        # Process video frames
        while True:
            # Read the next frame
            end, frame = video.read()
            if not end:
                break

            # Skip the first frame as we need two frames for comparison
            if previous_frame is None:
                previous_frame = frame
                continue

            # Compute the absolute difference between the current and previous frames
            frame_diff = cv2.absdiff(previous_frame, frame)

            # Convert the difference to grayscale
            frame_diff_gray = cv2.cvtColor(frame_diff, cv2.COLOR_BGR2GRAY)

            # Apply thresholding to emphasize the differences
            _, thresholded_diff = cv2.threshold(frame_diff_gray, 30, 255, cv2.THRESH_BINARY)

            # Count the number of white pixels in the difference image
            num_white_pixels = cv2.countNonZero(thresholded_diff)

            # If a slide change is detected, save the previous slide as a JPG image
            if num_white_pixels > frame.shape[0] * frame.shape[1] * 0.01:
                slide_counter += 1
                slide_filename = os.path.join(self.output_folder, f"slide{slide_counter}.jpg")
                cv2.imwrite(slide_filename, previous_frame)

            # Update the previous frame with the current frame for the next iteration
            previous_frame = frame
            frame_counter += 1

        # Save the last slide
        slide_counter += 1
        slide_filename = os.path.join(self.output_folder, f"slide{slide_counter}.jpg")
        cv2.imwrite(slide_filename, previous_frame)

        # Release the video capture
        video.release()
