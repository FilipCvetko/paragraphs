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

MENU_URL = "https://bestpractice.bmj.com/topics/en-gb/3000117/treatment-algorithm"

# logging.basicConfig(format='%(asctime)s::%(name)s::[%(levelname)s]::%(message)s', 
#                     filename=f"./logs/{datetime.datetime.now()}.log", 
#                     level=logging.INFO)

class BMJScraper():

    def __init__(self, num_diseases):
        logging.info("Initializing BMJScraper.")
        self.num_diseases = num_diseases # What fraction of BMJ do you want to scrape
        self.ROOT_URL = "https://bestpractice.bmj.com"
        self.INITIAL_URL = "https://bestpractice.bmj.com/specialties"
        self.storage_directory = "./scraped_data"

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
        specialties = self.specialties()
        logging.info(f"{len(specialties)} specialties loaded successfully.")
        diseases = []

        for specialty in specialties:
            new_diseases = self.diseases_from_specialty(specialty)
            logging.info(f"----> {len(new_diseases)} loaded from {specialty}.")
            for d in new_diseases:
                diseases.append(d)

        logging.info(f"{len(diseases)} diseases loaded successfully.")

        diseases = sample(diseases, self.num_diseases)
        logging.info("Diseases separated successfully.")

        for disease in diseases:
            menu_links = self.menu_links_from_disease(disease)
            logging.info(f" ----> Menu links for {disease} processed successfully..")
            for menu in menu_links:
                print(menu)
                content, heading = self.find_content(menu)
                logging.info(f" --------> Content for  {disease}/{heading} loaded successfully.")
                content = self.chunkText(content)
                self.store_content(content, heading)
                logging.info(f" --------> Content for  {disease}/{heading} stored successfully.")

    @log_errors
    def store_content(self, content, heading):       
        filename = f"{heading}/"
        full_foldername = os.path.join(self.storage_directory, filename)

        if os.path.isdir(full_foldername):
            with open(full_foldername + f"{hash(content[0])}.json", "w") as file:
                json.dump(content, file)
        else:
            os.mkdir(full_foldername)
            with open(full_foldername + f"{hash(content[0])}.json", "w") as file:
                json.dump(content, file)

        logging.info("Succesfully")

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
            if "Resources" in li.text:
                continue
            try:
                for item in li.ul.children:
                    print(item.a["href"])
                    menus_links.append(self.ROOT_URL + item.a["href"])
                    print(item.a.text)
            except:
                return menus_links

    @log_errors
    def preprocess_text(self, text):
        new_text = re.sub(r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?", "", text)
        new_text = re.sub(r"Practical tip", "", new_text)
        return new_text

    @log_errors
    def chunkText(self, text, max_tokens=512):
        """
            Content comes in list form. A list of all paragraph texts.
            List in, list out.
        """
        chunked_content = []
        num_tokens = 0
        new_content = ""

        for i, c in enumerate(text):
            new_tokens = len(c.split())
            num_tokens += new_tokens
            if num_tokens < max_tokens and i == len(text) - 1:
                chunked_content.append(new_content)
            elif num_tokens < max_tokens:
                new_content += (c + " ")
            else:
                chunked_content.append(new_content)
                num_tokens = 0
                new_content = ""

        return chunked_content

    @log_errors
    def find_content(self, menu_url):
        """
            Finds all paragraphs in the actual block of text,
            as denoted by "poce_contents" class of a div tag.
        """
        source = requests.get(menu_url).text
        soup = BeautifulSoup(source, "html.parser")

        heading = soup.main.h2.text

        content = []

        # Remove all references
        for span in soup.find_all("span", {"class" : "reference"}):
            span.decompose()

        # Find "poce contents in class" -> all text within is useful
        soup = soup.find("div", attrs={"class" : re.compile("poce_contents")})

        paragraphs = soup.find_all("p")
        for p in paragraphs:
            content.append(p.text)

        self.store_content(self.chunkText(content), heading)
        return content, heading


scraper = BMJScraper(num_diseases=100)
scraper.scrape()