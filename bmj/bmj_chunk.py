from bs4 import BeautifulSoup
from config import *
import os
import time

class BMJChunker():

    def __init__(self):
        self.pages_directory = PAGES_DIRECTORY
        self.chunks_directory = CHUNKS_DIRECTORY
        self.filenames = []

    def return_page_filenames(self):
        for root, dirs, files in os.walk(self.pages_directory, topdown=True):
            self.filenames = files
        return self.filenames

    def chunk_all_pages(self):
        for filename in self.filenames:
            self.chunk_page(self.pages_directory + filename)

    def chunk_page(self, page):
        with open(page, "r") as file:
            html = file.read()

        soup = BeautifulSoup(html, "html.parser")

        title = soup.find("h2").text
        if title == "Register with an access code":
            return

        # All important content is within div tags with class:card-block
        blocks = soup.find_all("div", attrs={"class" : "card-block"})

        

chunker = BMJChunker()
chunker.return_page_filenames()
chunker.chunk_all_pages()


# This function extracts meaningful data from HTML files and chunks them
# in appropriate ways to obtain data for evaluation or training.

# @log_errors
    # def store_content(self, content, heading):       
    #     filename = f"{heading}/"
    #     full_foldername = os.path.join(self.storage_directory, filename)

    #     if os.path.isdir(full_foldername):
    #         with open(full_foldername + f"{hash(content[0])}.json", "w") as file:
    #             json.dump(content, file)
    #     else:
    #         os.mkdir(full_foldername)
    #         with open(full_foldername + f"{hash(content[0])}.json", "w") as file:
    #             json.dump(content, file)

    #     logging.info("Succesfully")

# @log_errors
    # def preprocess_text(self, text):
    #     new_text = re.sub(r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?", "", text)
    #     new_text = re.sub(r"Practical tip", "", new_text)
    #     return new_text

    # @log_errors
    # def chunkText(self, text, max_tokens=512):
    #     """
    #         Content comes in list form. A list of all paragraph texts.
    #         List in, list out.
    #     """
    #     chunked_content = []
    #     num_tokens = 0
    #     new_content = ""

    #     for i, c in enumerate(text):
    #         new_tokens = len(c.split())
    #         num_tokens += new_tokens
    #         if num_tokens < max_tokens and i == len(text) - 1:
    #             chunked_content.append(new_content)
    #         elif num_tokens < max_tokens:
    #             new_content += (c + " ")
    #         else:
    #             chunked_content.append(new_content)
    #             num_tokens = 0
    #             new_content = ""

    #     return chunked_content

    # @log_errors
    # def find_content(self, menu_url):
    #     """
    #         Finds all paragraphs in the actual block of text,
    #         as denoted by "poce_contents" class of a div tag.
    #     """
    #     source = requests.get(menu_url).text
    #     soup = BeautifulSoup(source, "html.parser")

    #     heading = soup.main.h2.text

    #     content = []

    #     # Remove all references
    #     for span in soup.find_all("span", {"class" : "reference"}):
    #         span.decompose()

    #     # Find "poce contents in class" -> all text within is useful
    #     soup = soup.find("div", attrs={"class" : re.compile("poce_contents")})

    #     paragraphs = soup.find_all("p")
    #     for p in paragraphs:
    #         content.append(p.text)

    #     self.store_content(self.chunkText(content), heading)
    #     return content, heading