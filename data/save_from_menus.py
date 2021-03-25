# Iterates through all menu_links saved in menu_links.json and saves them 
# in orderly fashion with their FULL CORRESPONDING HTMLs !!!!!
# -> This way they could be more easily accessible by soup once free trial expires.

import json
import sys
import os
import logging
import datetime
import requests
from bs4 import BeautifulSoup
from config import *

class HTMLSaver():

    def __init__(self):
        logging.basicConfig(format='%(asctime)s::%(name)s::[%(levelname)s]::%(message)s', 
                    filename=f"{LOG_DIRECTORY}/saver_{datetime.datetime.now()}.log", 
                    level=logging.INFO)
        self.storage_directory = STORAGE_DIRECTORY
        self.menu_links_file = MENU_LINKS_FILE
        self.menu_links = None
        try:
            with open(self.menu_links_file, "r") as file:
                self.menu_links = json.load(file)
                print("Menu links loaded.")
        except FileNotFoundError:
            print("Menu links file not found. Run bmj_crawl.py first.")
            sys.exit(0)
        if not os.path.isdir(self.storage_directory):
            os.mkdir(self.storage_directory)
        logging.info("Successfully initialized HTMLSaver.")

    def save_page(self, url):
        try:
            source = requests.get(url).text
            soup = BeautifulSoup(source, "html.parser").prettify()
        except Exception as e:
            logging.exception('')

        # Save pretty soup object to a file with its content hashed.
        filename = str(hash(soup)) + ".html"
        with open(self.storage_directory + filename, "w") as file:
            json.dump(soup, file)

        logging.info(f"Successfully saved menu_link page: {url}")

    def save_all_menu_links(self):
        for link in self.menu_links:
            self.save_page(link)

saver = HTMLSaver()
saver.save_all_menu_links()