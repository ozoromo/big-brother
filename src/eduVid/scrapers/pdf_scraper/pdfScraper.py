from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import os
import sys
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "handle_presentation"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "question_answering"))
from slides_extractor import SlideExtractor
from qa_algo_core import HelperFN,SpeechRecog

class PdfScraper():
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

    def download_pdf(url, download_path, filename):
        # TODO: Change for pdfs...
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(os.path.join(download_path, filename), 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download: {url}")

    def scrap_pdfs(self, directory, courseId):
        chrome_options = Options()
        #chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")  
        # TODO

def Test():
    DOWNLOAD_PATH = "./video_dir"
    COURSE_ID = "38283"
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)
    # User input for password and username
    USERNAME = input("Enter your username: ")
    PASSWORD = input("Enter your password: ")

    # Initialize Selenium Scraper:
    pdf_scraper = PdfScraper()
    # Login to ISIS Website:
    try:
        # Gather educational pdfs from ISIS
        pdf_scraper.login(USERNAME,PASSWORD)
    finally:
        pdf_scraper.driver.quit()

def main():
    print("Do not run! Not Tested. May cause unexpected data overflow")

if __name__ == "__main__":
    main()
        