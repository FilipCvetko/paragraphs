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

class FrequencyClassifier():

    # Idea is to build a score. For each word that pops up in the text, add a score to
    # each of the 5 master headings if a word appears in those headings (their freqs)
    # At the end apply softmax function to the scores.

    def __init__(self, training_data_dir, test_data_dir):
        self.freqs_dir = None
        self.test_data_dir = test_data_dir
        self.training_data_dir = training_data_dir
        # with open(freqs_dir, "r") as file:
        #     self.freqs = json.load(file)
        self.test_data = pd.read_csv(test_data_dir)
        self.processed = self.test_data.dropna(how="all")
        self.correct = 0
        self.accuracy = None

    def freqs_from_training(self):
        data = pd.read_csv(self.training_data_dir)

        freqs = create_dict_from_text(unique_master_headings, data)
        freqs, counts = count_words_per_heading(freqs)
        print(counts)
        write_dict_to_file(freqs, "/reports")

        self.freqs = freqs


    def compare_against_json(self, word):
        """
            Return a dictionary with key = heading, value = score(word)
        """
        word_score = dict()
        for heading in unique_master_headings:
            if word in self.freqs[heading].keys():
                word_score[heading] = self.freqs[heading][word]
        
        return word_score

    def calculate_score(self):

        for i in range(len(self.processed)):
            # Step 1: Get master headings in a list to compare
            master_headings = get_headings(self.processed.iloc[i]["Heading"],master_only=True)

            # Step 2: Tokenize and stem text
            tokens = nltk.word_tokenize(self.processed.iloc[i]["Text"])

            # Step 3: Create a dict to count the scores
            scores = dict()
            for j in unique_master_headings:
                scores[j] = 0

            ps = PorterStemmer()

            for item in tokens:
                if item not in set(stopwords.words("english")) and item.isalnum():
                    item = ps.stem(item)

                    # Step 4: Compare token against JSON and return scores for each category in dict format
                    word_score = self.compare_against_json(item)

                    # Step 5: Update scores with the word_score
                    for heading in word_score.keys():
                        scores[heading] += word_score[heading]
            
            # Step 6: Evaluate
            prediction = max(scores, key=scores.get)
            if prediction in master_headings:
                self.correct += 1

    def print_acc(self):
        print("-----------------------")
        print("Final accuracy: ", float(self.correct) / float(len(self.processed)))
        print("-----------------------")

fc = FrequencyClassifier(training_data_dir=data_dir, test_data_dir=test_dir)
fc.freqs_from_training()
fc.calculate_score()
fc.print_acc()

