from bs4 import BeautifulSoup
from config import *
import os
import time
import re
import pandas as pd
import datetime
from tqdm import tqdm


class BMJChunker():

    def __init__(self):
        self.pages_directory = PAGES_DIRECTORY
        self.chunks_directory = CHUNKS_DIRECTORY
        self.filenames = self.return_page_filenames()
        self.data = []

    def return_page_filenames(self):
        for root, dirs, files in os.walk(self.pages_directory, topdown=True):
            return files

    def chunk_all_pages(self):
        all_cases = []
        for filename in self.filenames:
            try:
                cases, disease = self.chunk_page(self.pages_directory + filename)
            except TypeError:
                continue

            for case in cases:
                all_cases.append({"disease" : disease, "case" : case})
                if len(all_cases) > 200:
                    df = pd.DataFrame(all_cases)
                    df.to_csv("./../data/cases.csv")
                    return
            print(len(all_cases))

        df = pd.DataFrame(all_cases)
        df.to_csv("./../data/cases.csv")

    def save_chunk(self, text, disease, title):
        folder_dir = self.chunks_directory + title
        if not os.path.isdir(folder_dir):
            os.mkdir(folder_dir)
        with open(folder_dir + "/" + disease + str(hash(datetime.datetime.now()))[:10] + ".txt", "w") as file:
            file.write(text)

    def preprocess_text(self, text):
        text = re.sub(r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?", "", text)
        text = re.sub('[^A-Za-z0-9 \.\!\?]+', '', text)
        return text

    def find_block_style(self, block):
        # These numbers to correspond to styles declared in chunking_rules.txt
        if block.find("table"):
            return 4
        elif block.find("div", attrs={"class" : "row rowCondition"}):
            return 2
        elif block.find("div", attrs={"class" : re.compile("panel-content")}):
            return 3
        else:
            return 1


    def chunk_block_style1(self, block, disease, title):
        chunks = []
        if not block.find("h3"):
            # There is no reasonable separation
            chunk = block.get_text(separator=" ")
            chunks.append(chunk)
        else:
            for ind, h3 in enumerate(block.find_all("h3")):
                if ind == 0:
                    text = []
                    for item in h3.find_previous_siblings():
                        print(item)
                        text.append(item.get_text(separator=" "))
                    text.reverse()
                    first_chunk = " ".join(text)
                    if first_chunk != "":
                        chunks.append(first_chunk)
                    text = [h3.text]
                    for nextt in h3.find_next_siblings():
                        if nextt != "h3":
                            text.append(nextt.get_text(separator=" "))
                        else:
                            break
                    chunk = " ".join(text)
                    chunks.append(chunk)
                else:
                    text = [h3.text]
                    for nextt in h3.find_next_siblings():
                        if nextt != "h3":
                            text.append(nextt.get_text(separator=" "))
                        else:
                            break
                    chunk = " ".join(text)
                    chunks.append(chunk)

        for chunk in chunks:
            if chunk != "":
                self.save_chunk(chunk, disease, title)


    def chunk_block_style2(self, block, disease, title):
        # All rows inside one card-block constitute one chunk due to possible context loss.
        chunk = ""
        columns = False
        if block.find("div", attrs={"class" : re.compile("col-md")}):
            columns = True
        rows = block.find_all("div", attrs={"class" : "row rowCondition"})
        if rows == None:
            return 
        for row in rows:
            row_id = row.a["data-target"].split("#")[1]
            title = row.a.text
            collapsed_content = block.find("div", attrs={"id" : row_id})
            chunk += title
            chunk += " "
            if columns:
                # There are columns -> stack them left to right (top -> bottom)
                pass
            else:
                # No columns
                pass
    def maxN(self, text, max_tokens=512):
        """
            Text in, text out.
        """
        tokens = text.split()
        out_content = []
        if len(tokens) > max_tokens - 3:
            for i in range(max_tokens - 20):
                out_content.append(tokens[i])
        else:
            return text

        return " ".join(out_content)

    def chunk_page(self, page):
        with open(page, "r") as file:
            html = file.read()
        soup = BeautifulSoup(html, "html.parser")
        try:
            if soup.find("h2").text != "Summary":
                title = soup.find("link", attrs={"rel" : "canonical"})["href"].rsplit("/")[-1]
            else:
                title = "summary"
            disease = soup.find("h1").text
        except AttributeError:
            return
        if title == "Register with an access code":
            return
        if "Subscription required" in disease:
            return
        for span in soup.find_all("span", {"class" : "reference"}):
            span.decompose()
        for span in soup.find_all("span", {"class" : "figureWrap"}):
            span.decompose()

        # All important content is within div tags with class:card-block
        blocks = soup.find_all("div", attrs={"class" : "card-block"})

        for block in blocks:
            if "disclaimer" in block.text or "Disclosures" in block.text or "VIEW ALL" in block.text:
                continue
            # style = self.find_block_style(block)
            # if style == 1:
            #     chunks = self.chunk_block_style1(block, disease, title)
            # elif style == 2:
            #     pass
            # elif style == 3:
            #     pass
            # else:
            #     pass
            # text = ""
            # for p in block.find_all("p"):
            #     text += p.get_text(separator=" ")
            # text = self.maxN(text)
            # text = self.preprocess_text(text)
            # if len(text.split()) > 20:
            #     print(text)
            #     time.sleep(2)
            #     self.data.append({"disease" : disease, "heading" : title, "content" : text})

            # if title == "case-history":
            #     text = block.get_text()
            #     text = text.replace(" #1", "")
            #     text = text.replace(" #2", "")
            #     text = text.replace(" #3", "")
            #     cases = text.split("Case history")
            #     cases = [case for case in cases if len(case) != 0]
            if title == "case-history":
                sections = block.find_all("section")
                cases = []
                for section in sections:
                    if "Case history" in section.h3.text:
                        case = section.p.text
                        cases.append(case)
                return cases, disease



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