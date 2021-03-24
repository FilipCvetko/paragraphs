import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import time
import json
import os
import logging
import datetime
from functools import wraps
from random import sample

DISEASE_URL = "https://bestpractice.bmj.com/topics/en-gb/36"

class BMJCrawler():

    def __init__(self, fraction_flag, num_diseases):
        logging.basicConfig(format='%(asctime)s::%(name)s::[%(levelname)s]::%(message)s', 
                    filename=f"./logs/{datetime.datetime.now()}.log", 
                    level=logging.INFO)
        logging.info("Initializing BMJScraper.")
        self.num_diseases = num_diseases # What fraction of BMJ do you want to scrape
        self.ROOT_URL = "https://bestpractice.bmj.com"
        self.INITIAL_URL = "https://bestpractice.bmj.com/specialties"
        self.storage_directory = "./scraped_data"
        self.disease_links_filename = "./disease_links.json"
        self.menu_links_filename = "./menu_links.json"
        self.fraction_flag = fraction_flag

    def log_errors(original_function):
        """
            This function is a wrapper function for all scraper functions
            It works by trying to execute the function and if it fails, it logs the
            error thrown to the function to the log file.
        """
        @wraps(original_function)
        def wrapper_function(*args, **kwargs):
            try:
                return original_function(*args, **kwargs)
            except:
                logging.exception('')
        return wrapper_function

    def scrape(self):
        if not os.path.isfile(self.disease_links_filename):
            with open(self.disease_links_filename, "w") as file:

                specialties = self.specialties()
                logging.info(f"{len(specialties)} specialties loaded successfully.")
                diseases = []

                for specialty in specialties:
                    new_diseases = self.diseases_from_specialty(specialty)
                    logging.info(f"----> {len(new_diseases)} loaded from {specialty}.")
                    for d in new_diseases:
                        diseases.append(d)

                logging.info(f"{len(diseases)} diseases loaded successfully.")
                json.dump(diseases, file)
                logging.info("Disease save to file successfully.")
        else:
            with open(self.disease_links_filename, "r") as file:
                diseases = json.load(file)
                logging.info(f"{len(diseases)} diseases loaded from file.")

        if self.fraction_flag == True:
            diseases = sample(diseases, self.num_diseases)
            logging.info("Diseases separated successfully.")

        if not os.path.isfile(self.menu_links_filename):
            all_menu_links = []
            for disease in diseases:
                menu_links = self.menu_links_from_disease(disease)
                for link in menu_links:
                    all_menu_links.append(link)
                logging.info(f" ----> Menu links for {disease} processed successfully..")

            logging.info(f"Finished with {len(all_menu_links)} menu links from {len(diseases)} diseases selected at random.")

            with open(self.menu_links_filename, "w") as file:
                json.dump(all_menu_links, file)
                logging.info(f"Saved {len(all_menu_links)} links to file.")
        else:
            with open(self.menu_links_filename, "r") as file:
                all_menu_links = json.load(file)
                logging.info(f"Loaded {len(all_menu_links)} links from file.")

        # At this point you have all_menu_links with approximately 80k urls.

    @log_errors
    def specialties(self):
        """
            Return https url links to all specialtis on bmj
        """
        source = requests.get(self.INITIAL_URL).text
        soup = BeautifulSoup(source, "html.parser")
        specialties_links = []

        tag_list = soup.find("ul", attrs={"class":"specialty-list list-unstyled"})

        for li in tag_list.children:
            try:
                if li.text == "Assessments" or li.text == "Overviews":
                    return specialties_links
            except:
                return specialties_links
            specialties_links.append(self.ROOT_URL + li.a["href"])

    @log_errors 
    def diseases_from_specialty(self, specialty_url):
        source = requests.get(specialty_url).text
        soup = BeautifulSoup(source, "html.parser")
        diseases_links = []

        tag_list = soup.find_all("a", attrs={"class":"d-flex align-items-center"})
        for tag in tag_list:
            diseases_links.append(self.ROOT_URL + tag["href"])

        return diseases_links

    @log_errors
    def menu_links_from_disease(self, disease_url):
        source = requests.get(disease_url).text
        soup = BeautifulSoup(source, "html.parser")
        menus_links = []

        menu = soup.find("ul", attrs={"id" : "menus"})
        for submenu in menu.children:
            if "Resources" in submenu.text or "Summary" in submenu.text:
                continue
            try:
                for item in submenu.ul.children:
                    menus_links.append(self.ROOT_URL + item.a["href"])
            except:
                return menus_links

        return menus_links

scraper = BMJCrawler(fraction_flag=True, num_diseases=10)
scraper.scrape()