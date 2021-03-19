import pandas as pd
import nltk
from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import json
from tqdm import tqdm

def get_headings(text, master_only=True):
    """
        Returns annotated headings from text in a list form.
        If master_only is set to True, it will return
        only 
    """
    if text == None:
        return NoneType
    else:
        if text.find(","):
            headings = text.split(",")
        else:
            headings = list(text)

        if master_only == False:
            return headings
        else:
            final_headings = list()
            for heading in headings:
                if heading.split("/")[0] not in final_headings:
                    final_headings.append(heading.split("/")[0])
            return final_headings

def create_dict_from_text(unique_master_headings, data, master_only=True):
    """
        Unique master headings are found in config.py
        Data is a pandas object

        Returns a dict
    """
    nltk.download("punkt")
    nltk.download("stopwords")

    ps = PorterStemmer()

    frequencies = dict()

    for i in unique_master_headings:
        frequencies[i] = dict()

    for i in tqdm(range(len(data))):
        master_headings = get_headings(data.iloc[i]["Heading"],master_only=master_only)
        text = data.iloc[i]["Text"]
        tokens = word_tokenize(text)
        for item in tokens:
            if item not in set(stopwords.words("english")) and item.isalnum():
                item = ps.stem(item)
                for heading in master_headings:
                    if item not in frequencies[heading].keys():
                        frequencies[heading][item] = 1
                    else:
                        frequencies[heading][item] += 1

    return frequencies

def write_dict_to_file(dictionary, dir):
    """
        Takes dict and writes a json file in dir directory.
        Also sorts the subdictionaries in descending order.
        Returns dictionary back.
    """
    for heading in dictionary.keys():
	    dictionary[heading] = {k: v for k,v in sorted(dictionary[heading].items(), reverse=True, key=lambda item:item[1])}

    with open(f".{dir}/freqs.json", "w") as file:
        json.dump(dictionary, file, indent=4)

    return dictionary

def count_words_per_heading(dictionary):
    """
        Counts words per each heading and divides by the sum.
        Dict in dict out.
        Returns dict.
    """
    heading_counts = dict()
    for heading in dictionary.keys():
        summa = 0
        for item in dictionary[heading].keys():
            summa += dictionary[heading][item]
        heading_counts[heading] = summa

        for item in dictionary[heading].keys():
            dictionary[heading][item] = float(dictionary[heading][item])/float(heading_counts[heading])


    return dictionary, heading_counts

def confusion_matrix(targets, outputs, headings):
    """
        Takes a list of all targets and outputs (list of lists)
        and creates a confusion matrix.
    """
    # 