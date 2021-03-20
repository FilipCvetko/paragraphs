import requests
from bs4 import BeautifulSoup
import re
import time

INITIAL_URL = "https://bestpractice.bmj.com/specialties"
ROOT_URL = "https://bestpractice.bmj.com"
SPECIALTY_URL ="https://bestpractice.bmj.com/specialties/1/Allergy-and-immunology"
DISEASE_URL = "https://bestpractice.bmj.com/topics/en-gb/596"
MENU_URL = "https://bestpractice.bmj.com/topics/en-gb/3000117/treatment-algorithm"
CONTENT_THRESHOLD = 3

def specialties(url):
    """
        Return https url links to all specialtis on bmj
    """
    source = requests.get(url).text
    soup = BeautifulSoup(source, "html.parser")
    specialties_links = []

    tag_list = soup.find("ul", attrs={"class":"specialty-list list-unstyled"})

    for li in tag_list.children:
        try:
            if li.text == "Assessments" or li.text == "Overviews":
                return specialties_links
        except:
            return specialties_links
        specialties_links.append(ROOT_URL + li.a["href"])

def diseases_from_specialty(specialty_url):
    source = requests.get(specialty_url).text
    soup = BeautifulSoup(source, "html.parser")
    diseases_links = []

    tag_list = soup.find_all("a", attrs={"class":"d-flex align-items-center"})
    for tag in tag_list:
        diseases_links.append(ROOT_URL + tag["href"])

    return diseases_links

def menu_links_from_disease(disease_url):
    source = requests.get(disease_url).text
    soup = BeautifulSoup(source, "html.parser")
    menus_links = []

    menu = soup.find("ul", attrs={"id" : "menus"})
    for li in menu.children:
        if "Resources" in li.text:
            continue
        try:
            for item in li.ul.children:
                menus_links.append(ROOT_URL + item.a["href"])
                print(item.a.text)
        except:
            return menus_links

def preprocess_text(text):
    new_text = re.sub(r"^http:", "", text)
    new_text = re.sub(r"Practical tip", "", new_text)
    return new_text

def find_content(menu_url):
    source = requests.get(menu_url).text
    soup = BeautifulSoup(source, "html.parser")

    content = []

    # Remove all references
    for span in soup.find_all("span", {"class" : "reference"}):
        span.decompose()

    # Find "poce contents in class"

    divs = soup.find_all("div")
    for div in divs:
        num_of_content = 0
        for child in div.children:
            if child.name == 0:
                break
            if child.name == "p" or child.name == "ul":
                num_of_content += 1

        if num_of_content > CONTENT_THRESHOLD:
            corrected_text = preprocess_text(str(div.text))
            content.append(corrected_text)

    return content

print(find_content(MENU_URL)[0])