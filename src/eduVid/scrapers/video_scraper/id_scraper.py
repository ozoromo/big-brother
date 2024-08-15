from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import os
import sys
import json
import requests
import time
from getpass import getpass

class IdScraper():
    """
    A class to scrape course IDs from the TU Berlin ISIS platform.

    Methods:
    __init__ -- Initializes the WebDriver and WebDriverWait objects.
    capture_screenshot -- Captures a screenshot of the current browser window (for debugging).
    login -- Logs in to the ISIS platform using provided credentials.
    logout -- Logs out from the ISIS platform.
    scrap_ids -- Scrapes course IDs and names from a specified directory on the ISIS platform.
    """
    def __init__(self) -> None:
        """
        Initializes the IdScraper class with WebDriver and WebDriverWait objects.
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

    def scrap_ids(self, directory):
        """
        Scrapes course IDs and names from a specified directory on the ISIS platform.

        Arguments:
        directory -- string, the path where the scraped data will be saved.

        """
        chrome_options = Options()
        #chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")  

        # for now only Faculty IV
        seite_dir = "https://isis.tu-berlin.de/course/index.php?categoryid=177"
        
        self.driver.get(seite_dir)   

        try:
            links = self.driver.find_elements(By.CSS_SELECTOR, 'div.category.notloaded.with_children.collapsed a')
        except TimeoutException:
            print("No institutes found")

        hrefs = [link.get_attribute('href') for link in links]
        names = [link.text for link in links]

        courses_data = []

        for index, link in enumerate(hrefs):
            try:
                name = names[index]
                # Create new institut inside json 
                institute_entry = next((item for item in courses_data if item['name'] == name), None)
                if not institute_entry:
                    institute_entry = {
                        'name': name,
                        'courses': []
                    }
                    courses_data.append(institute_entry)

                self.driver.get(link)
                time.sleep(3)

                course_elements = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.coursebox'))
                )

                for course in course_elements:
                    course_id = course.get_attribute('data-courseid')
                    course_name = course.find_element(By.CSS_SELECTOR, 'div.coursename > a').text
                    
                    institute_entry['courses'].append({
                        "course_id": course_id,
                        "course_name": course_name
                    })

                # Find if other pages exists for more courses
                try:
                    mehr_anzeigen_button = self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "paging")]//a[contains(text(), "Mehr anzeigen")]')))
                    mehr_anzeigen_button.click()
                    i = 1
                    while True:
                        print("On page ",i)
                        course_elements = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "coursebox")]')))
                        if len(course_elements) == 0:
                            break

                        for course in course_elements:
                            course_id = course.get_attribute('data-courseid')
                            course_name = course.find_element(By.CSS_SELECTOR, 'div.coursename > a').text
                            
                            institute_entry['courses'].append({
                                "course_id": course_id,
                                "course_name": course_name
                            })
                        i += 1
                        
                        try:
                            next_page = self.wait.until(EC.presence_of_element_located((By.XPATH, '//li[contains(@class, "page-item")]//a[contains(@class, "page-link") and span[contains(text(), "»")]]')))
                            next_page_link = next_page.get_attribute('href')
                            self.driver.get(next_page_link)
                        except TimeoutException:
                            print("Next page link not found")
                            break

                except TimeoutException:
                    print("Mehr anzeigen button not found")

                self.driver.get(link)
                time.sleep(3)

                # Get all archieved modules from WS 23/24
                try:
                    archivebereich = self.driver.find_element(By.XPATH, '//div[contains(@class, "category")]//a[contains(text(), "Archivbereich")]')
                    archiv_link = archivebereich.get_attribute('href')
                    self.driver.get(archiv_link)

                    ws23 = self.driver.find_element(By.XPATH, '//div[contains(@class, "category")]//a[contains(text(), "WS23/24")]')
                    self.driver.get(ws23.get_attribute('href'))

                    course_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.coursebox')
                    for course in course_elements:
                        course_id = course.get_attribute('data-courseid')
                        course_name = course.find_element(By.CSS_SELECTOR, 'div.coursename > a').text
                        
                        institute_entry['courses'].append({
                            "course_id": course_id,
                            "course_name": course_name
                        })

                    self.driver.get(archiv_link)

                    ss23 = self.driver.find_element(By.XPATH, '//div[contains(@class, "category")]//a[contains(text(), "SS23")]')
                    self.driver.get(ss23.get_attribute('href'))

                    course_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.coursebox')
                    for course in course_elements:
                        course_id = course.get_attribute('data-courseid')
                        course_name = course.find_element(By.CSS_SELECTOR, 'div.coursename > a').text
                        
                        institute_entry['courses'].append({
                            "course_id": course_id,
                            "course_name": course_name
                        })

                except Exception as e:
                    print(f"Error processing archived modules for {name}: {e}")

            except Exception as e:
                print(f"Error processing institut: {name}: {e}")
        
        with open(directory, 'w', encoding='utf-8') as f:
            json.dump(courses_data, f, ensure_ascii=False, indent=4)

            
def scrape_ids():
    DOWNLOAD_PATH = "course_ids.json"
    # User input for password and username
    USERNAME = input("Enter your username: ")
    PASSWORD = getpass()
    

    # Initialize Selenium Scraper:
    video_scraper = IdScraper()
    # Login to ISIS Website:
    try:
        # Gather ids of modules
        video_scraper.login(USERNAME,PASSWORD)
        video_scraper.scrap_ids(DOWNLOAD_PATH)

        video_scraper.logout()

    finally:
        video_scraper.driver.quit()


        