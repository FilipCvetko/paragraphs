# Iterates through all menu_links saved in menu_links.json and saves them 
# in orderly fashion with their FULL CORRESPONDING HTMLs !!!!!
# -> This way they could be more easily accessible by soup once free trial expires.

import json
import sys
import os
import logging
import datetime
import time
import requests
from bs4 import BeautifulSoup
from config import *
from credentials import *
from requests.auth import HTTPBasicAuth
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import scrapy
driver = webdriver.Chrome()

class HTMLSaver():

    def __init__(self):
        logging.basicConfig(format='%(asctime)s::%(name)s::[%(levelname)s]::%(message)s', 
                    filename=f"{LOG_DIRECTORY}/saver_{datetime.datetime.now()}.log", 
                    level=logging.INFO)
        self.storage_directory = STORAGE_DIRECTORY
        self.menu_links_file = MENU_LINKS_FILE
        self.menu_links = None
        self.disease_links_file = DISEASE_LINKS_FILE
        self.disease_links = None
        self.username = BMJ_USERNAME
        self.password = BMJ_PASSWORD
        self.login_page = LOGIN_PAGE
        self.visited_filename = VISITED_FILENAME
        self.visited = None
        try:
            with open(self.menu_links_file, "r") as file:
                self.menu_links = json.load(file)
                print("Menu links loaded.")
        except FileNotFoundError:
            print("Menu links file not found. Run bmj_crawl.py first.")
            sys.exit(0)
        if not os.path.isdir(self.storage_directory):
            os.mkdir(self.storage_directory)
        try:
            with open(self.disease_links_file, "r") as file:
                self.disease_links = json.load(file)
                print("Disease links loaded.")
        except FileNotFoundError:
            print("Menu links file not found. Run bmj_crawl.py first.")
            sys.exit(0)
        if not os.path.isfile(self.visited_filename):
            self.visited = self.create_dict_from_menus()
            with open(self.visited_filename, "w") as file:
                json.dump(self.visited, file)
                logging.info("Created visited.json file")
        else:
            with open(self.visited_filename, "r") as file:
                self.visited = json.load(file)
                logging.info("Successfully read visited.json file.")
        logging.info("Successfully initialized HTMLSaver.")
        logging.info(f"{self.check_num_visited()} already visited and saved out of {len(self.visited)}")

    def check_num_visited(self):
        total = 0
        for key, value in self.visited.items():
            if value == True:
                total += 1
        return total

    def create_dict_from_menus(self):
        visited = dict()
        for link in self.menu_links:
            visited[link] = False
        return visited

    def save_page(self, html):
        filename = str(hash(datetime.datetime.now())) + ".html"
        with open(self.storage_directory + filename, "w") as file:
            file.write(html)

    def save_json(self):
        with open(self.visited_filename, "w") as file:
            json.dump(self.visited, file)

    def save_all_menu_links(self):
        driver.get(self.login_page)
        driver.find_element_by_xpath('//button[text()="Accept Cookies"]').click()
        driver.find_element_by_id("lfInputEmail").send_keys(BMJ_USERNAME)
        driver.find_element_by_id ("lfInputPass").send_keys(BMJ_PASSWORD)
        driver.find_element_by_id("loginSubmit").click()

        for link in self.menu_links:
            base_link = link.rsplit("/", 1)[-2]
            if base_link not in self.visited:
                self.visited[base_link] = False
            if self.visited[base_link] == True and self.visited[link] == True:
                continue
            driver.get(base_link)
            if self.visited[base_link] == False:
                self.save_page(driver.execute_script("return document.documentElement.outerHTML"))
                logging.info(f"----> Successfully saved page {base_link}")
                self.visited[base_link] = True
                self.save_json()
            if self.visited[link] == False:
                driver.get(link)
                self.save_page(driver.execute_script("return document.documentElement.outerHTML"))
                logging.info(f"----> Successfully saved page {link}")
                self.visited[link] = True
                self.save_json()
            
           

saver = HTMLSaver()
saver.save_all_menu_links()