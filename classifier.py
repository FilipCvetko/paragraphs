import pandas as pd
from medwise_utils import *
from config import *
import time
import nltk
import json
from tqdm import tqdm
from nltk.corpus import stopwords
from scipy.special import softmax
import numpy as np
nltk.download("punkt")
nltk.download("stopwords")

with open("./reports/freqs.json", "r") as file:
    freqs = json.load(file)

def compare_against_json(freqs, word):
    """
        Return a dictionary with key = heading, value = score(word)
    """
    word_score = dict()
    for heading in unique_master_headings:
        if word in freqs[heading].keys():
            word_score[heading] = freqs[heading][word]
    
    return word_score



test_data = pd.read_csv("~/IT/DS/medwise/paragraphs/data/test.csv")

# Idea is to build a score. For each word that pops up in the text, add a score to
# each of the 5 master headings if a word appears in those headings (their freqs)
# At the end apply softmax function to the scores.

processed = test_data.dropna(how="all")

correct = 0

for i in range(len(processed)):
    # print(processed.iloc[i]["Heading"])

    # Step 1: Get master headings in a list to compare
    master_headings = get_headings(processed.iloc[i]["Heading"],master_only=True)

    # Step 2: Tokenize and stem text
    tokens = nltk.word_tokenize(processed.iloc[i]["Text"])

    # Step 3: Create a dict to count the scores
    scores = dict()
    for j in unique_master_headings:
        scores[j] = 0

    ps = PorterStemmer()

    for item in tokens:
        if item not in set(stopwords.words("english")) and item.isalnum():
            item = ps.stem(item)

            # Step 4: Compare token against JSON and return scores for each category in dict format
            word_score = compare_against_json(freqs, item)

            # Step 5: Update scores with the word_score
            for heading in word_score.keys():
                scores[heading] += word_score[heading]


    print("-----------------------")
    print(processed.iloc[i]["Text"], "\n\n", master_headings, "\n")
    print("Highest score: ", max(scores, key=scores.get))
    print("-----------------------")
    
    # Step 6: Evaluate
    if max(scores, key=scores.get) in master_headings:
        correct += 1

print("Final accuracy: ", float(correct) / float(len(processed)))

