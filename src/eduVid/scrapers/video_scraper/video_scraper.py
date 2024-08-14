from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import os
import json
import requests
import time
from getpass import getpass

class VideoScraper():
    """
    A class to scrape videos from the TU Berlin ISIS platform.

    Methods:
    __init__ -- Initializes the WebDriver and WebDriverWait objects.
    capture_screenshot -- Captures a screenshot of the current browser window (for debugging).
    login -- Logs in to the ISIS platform using provided credentials.
    logout -- Logs out from the ISIS platform.
    setup_session_with_cookies -- Sets up a requests session with cookies from the Selenium WebDriver.
    download_video -- Downloads a video from the provided URL to the specified directory.
    scrap_videos -- Scrapes video URLs from a specific course and downloads them.
    """
    def __init__(self) -> None:
        """
        Initializes the VideoScraper class with WebDriver and WebDriverWait objects.
        """
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.wait_long = WebDriverWait(self.driver, 20)

    # For Debugging...
    def capture_screenshot(driver, filename):
        """
        Captures a screenshot of the current browser window.

        Arguments:
        driver -- WebDriver object controlling the browser.
        filename -- string, the path where the screenshot will be saved.

        """
        driver.save_screenshot(filename)

    def login(self, username, password):
        """
        Logs in to the ISIS platform using provided username and password.

        Arguments:
        username -- string, the username for logging in.
        password -- string, the password for logging in.

        """
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
        """
        Logs out from the ISIS platform.

        """
        self.driver.set_page_load_timeout(5)
        logout_button = self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Logout')))
        logout_button.click()
        print("Logout complete.")
    
    # Cookies müssen aktiviert werden laut ISIS-Webseite
    def setup_session_with_cookies(self):
        """
        Sets up a requests session with cookies from the Selenium WebDriver.

        Returns:
        session -- a requests.Session object with cookies set.
        """
        session = requests.Session()
        for cookie in self.driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
        return session

    def download_video(self, session, url, download_path, filename):
        """
        Downloads a video from the provided URL to the specified directory.

        Arguments:
        session -- requests.Session object with cookies.
        url -- string, the URL of the video to download.
        download_path -- string, the directory where the video will be saved.
        filename -- string, the name of the file to save the video as.

        """
        response = session.get(url, stream=True)
        if response.status_code == 200:
            with open(os.path.join(download_path, filename), 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download: {url}")

    def scrap_videos(self, directory, courseId):
        """
        Scrapes video URLs from a specific course and downloads them.

        Arguments:
        directory -- string, the directory where the course videos will be saved.
        courseId -- string, the ID of the course to scrape videos from.

        """
        chrome_options = Options()
        #chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")  

        course_dir = os.path.join(directory, courseId)

        #create folder for the course
        if not os.path.exists(course_dir):
            # Create the folder
            os.makedirs(course_dir)
            print(f"Folder created: {course_dir}")
        else:
            print(f"Folder already exists: {course_dir}")
        
        self.driver.get(f"https://isis.tu-berlin.de/mod/videoservice/view.php/course/{courseId}/browse")
        session = self.setup_session_with_cookies()
        try:
            links = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.thumbnail-container a')))
        except TimeoutException:
            print("No videos found under ", courseId)
            return
        
        hrefs = [link.get_attribute('href') for link in links]

        if len(hrefs) > 30:
            print("Too much videos found under ", courseId, ". Please check and confirm to process further: ")
            confirmation = input("To continue enter 1: ")
            if confirmation != "1":
                print("Skipping videos from course: ", courseId)
                return


        for index, link in enumerate(hrefs):
            try:
                self.driver.get(link)
                time.sleep(3)
                video = self.driver.find_element(By.TAG_NAME, 'video')
                video_url = video.get_attribute('src')
                if video_url:
                    video_dir = os.path.join(course_dir, f"video_{index + 1}")
                    # Create directories for videos
                    if not os.path.exists(video_dir):
                        os.makedirs(video_dir)
                        print(f"Folder created: {video_dir}")
                    # Download video
                    self.download_video(session, video_url, video_dir, f"video_{index + 1}.mp4")
            except Exception as e:
                print(f"Error processing video {courseId}_{index + 1}: {e}")

def scrape_all_videos():
    """
    A function to scrape all videos from courses listed in 'course_ids_selbst.json' and save them to the specified directory.
    
    """
    DOWNLOAD_PATH = "./video_dir"

    with open('course_ids_selbst.json', 'r', encoding='utf-8') as f:
        courses_data = json.load(f)

    all_course_ids = []
    all_institut_names = []

    for institute in courses_data:
        for course in institute['courses']:
            all_course_ids.append(course['course_id'])
            all_institut_names.append(institute['name'])

    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)
    # User input for password and username
    USERNAME = input("Enter your username: ")
    PASSWORD = getpass()

    # Initialize Selenium Scraper:
    video_scraper = VideoScraper()
    # Login to ISIS Website:
    try:
        video_scraper.login(USERNAME,PASSWORD)
        for i, course_id in enumerate(all_course_ids):
            # Gather educational videos from ISIS
            institut_dir = os.path.join(DOWNLOAD_PATH, all_institut_names[i])
            video_scraper.scrap_videos(institut_dir, course_id)

        video_scraper.logout()

    finally:
        video_scraper.driver.quit()

if __name__ == "__main__":
    scrape_all_videos()