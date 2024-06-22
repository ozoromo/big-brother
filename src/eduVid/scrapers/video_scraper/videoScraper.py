from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from bs4 import BeautifulSoup
from bs4.element import NavigableString

import os
import sys
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "handle_presentation"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "question_answering"))
from slides_extractor import SlideExtractor
from slides_ocr import SlideOCR
from qa_algo_core import HelperFN,SpeechRecog

class VideoScraper():
    def __init__(self) -> None:
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)

    # For Debugging...
    def capture_screenshot(driver, filename):
        driver.save_screenshot(filename)

    def login(self, username, password):

        print("Navigating to login page...")
        self.driver.get("https://isis.tu-berlin.de/login/index.php")

        tu_login_button = self.wait.until(EC.presence_of_element_located((By.ID, 'shibbolethbutton')))
        tu_login_button.click()

        print("Entering username...")
        username_field = self.wait.until(EC.presence_of_element_located((By.ID, 'username')))
        print("Entering password...")
        
        password_field = self.wait.until(EC.presence_of_element_located((By.ID, 'password')))

        username_field.send_keys(username)
        password_field.send_keys(password)

        login_button = self.wait.until(EC.presence_of_element_located((By.ID, 'login-button')))
        login_button.click()

        print("Login complete.")

    def logout(self):
        self.driver.set_page_load_timeout(5)
        logout_button = self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Logout')))
        logout_button.click()
        print("Logout complete.")

    def download_video(url, download_path, filename):
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(os.path.join(download_path, filename), 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download: {url}")

    def scrap_videos(self, directory, courseId):
        chrome_options = Options()
        #chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")  

        wait = WebDriverWait(self.driver, 10)

        course_dir = os.path.join(directory, courseId)

        #create folder for the course
        if not os.path.exists(course_dir):
            # Create the folder
            os.makedirs(course_dir)
            print(f"Folder created: {course_dir}")
        else:
            print(f"Folder already exists: {course_dir}")
        
        self.driver.get(f"https://isis.tu-berlin.de/mod/videoservice/view.php/course/{courseId}/browse")

        video_items = self.driver.find_element(By.CLASS_NAME, 'video-item')

        for index, item in enumerate(video_items):
            try:
                video = item.find_element(By.TAG_NAME, 'video')
                video_url = video.get_attribute('src')
                if video_url:
                    video_dir = os.path.join(course_dir, f"video_{index + 1}")
                    slides_dir = os.path.join(video_dir, "slides")
                    # Create directories for video and slides
                    if not os.path.exists(video_dir):
                        os.makedirs(video_dir)
                        print(f"Folder created: {video_dir}")
                    if not os.path.exists(slides_dir):
                        os.makedirs(slides_dir)
                        print(f"Folder created: {slides_dir}")
                    # Download video
                    self.download_video(video_url, video_dir, f"video_{index + 1}.mp4")
            except Exception as e:
                print(f"Error processing video {courseId}_{index + 1}: {e}")

def Test():
    DOWNLOAD_PATH = "./video_dir"
    COURSE_ID = "38283"
    TESSERACT_PATH = '/opt/homebrew/bin/tesseract' # PATH TO TESSERACT DIRECTORY
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)
    # User input for password and username
    USERNAME = input("Enter your username: ")
    PASSWORD = input("Enter your password: ")

    # Initialize Selenium Scraper:
    video_scraper = VideoScraper()
    # Login to ISIS Website:
    try:
        # Gather educational videos from ISIS
        video_scraper.login(USERNAME,PASSWORD)
        video_scraper.scrap_videos(DOWNLOAD_PATH, COURSE_ID)

        course_dir = os.path.join(DOWNLOAD_PATH, COURSE_ID)
        video_dirs = [os.path.join(course_dir, f) for f in os.listdir(course_dir) if os.path.isdir(os.path.join(course_dir, f))]

        for video_dir in video_dirs:
            video_file = os.path.join(video_dir, f"{os.path.basename(video_dir)}.mp4")
            slides_dir = os.path.join(video_dir, "slides")
            # multiprocessing to fasten?
            # Mp4 Video -> Mp3 Wav *-> Txt Text *[s2t Algorithm]
            audio_file = video_file.replace('.mp4', '.wav')
            helper = HelperFN()
            helper.extract_audio_from_mp4(video_file, audio_file)
            recog = SpeechRecog(audio_file)
            context, tags = recog.transcribe()
            # Mp4 Video -> Png Slide
            extractor = SlideExtractor(video_file, slides_dir)
            extractor.extract_slides_from_video()

            # Png Slide -> Txt Slide [SlideOCR]
            # TODO: More accurate and efficient OCR of Slides
            slide_ocr = SlideOCR(TESSERACT_PATH, slides_dir)
            slide_text = slide_ocr.ocr_text_from_slides()

            # TODO: Themen Extraktion für Indexierung

            video_data = {
                "video_file": video_file,
                "video_skript": context,
                "tags": tags,
                "slide_context": slide_text
            }
            # TODO: Where to save the gathered datas ?
        video_scraper.logout()

    finally:
        video_scraper.driver.quit()

def main():
    print("Do not run! Not Tested. May cause unexpected data overflow")

if __name__ == "__main__":
    main()
        