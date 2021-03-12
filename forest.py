import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from medwise_utils import *
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import nltk
from tqdm import tqdm
import time
import random
from config import *

class ForestClassifier():

    def __init__(self, data_path, test_path):
        self.data = pd.read_csv(data_path)
        self.headings = self.data["Heading"].tolist()
        self.data = self.data["Text"].tolist()
        self.test = pd.read_csv(test_path).dropna(how="all")
        self.test = self.test.sample(frac=1)
        self.sleep_time = 3
        

    def preprocess_headings(self):

        new_list = []
        for item in self.headings:
            headings = get_headings(item)
            temp = 0
            if "Overview" in headings:
                temp = 1
            if "Presentation" in headings:
                temp = 2
            if "Diagnosis" in headings:
                temp = 3
            if "Management" in headings:
                temp = 4
            if "Follow up" in headings:
                temp = 5
            if "Others" in headings:
                temp = 6

            new_list.append(temp)

        self.headings = new_list
        return new_list

    def preprocess_text(self):

        stemmer = WordNetLemmatizer()

        for ind, val in tqdm(enumerate(self.data)):
            tokens = nltk.word_tokenize(val)
            new_tokens = []
            
            for token in tokens:
                if token not in set(stopwords.words("english")) and token.isalnum():
                    token = stemmer.lemmatize(token)
                    new_tokens.append(token)

            self.data[ind] = " ".join(new_tokens)
        
        return self.data

    def forest_classify(self):

        vectorizer = CountVectorizer(max_features=1500, min_df=5, max_df=0.7, stop_words=stopwords.words('english'))
        X = vectorizer.fit_transform(self.data).toarray()

        clf = RandomForestClassifier(max_depth=100)
        clf.fit(X,self.headings)

        for i, item in enumerate(self.test["Text"]):
            print(item)
            print("--------------------------")
            print("Predicted: ", clf.predict(vectorizer.transform([item]).toarray()))
            print("Actual: ", self.test.iloc[i]["Heading"])
            print("--------------------------")
            time.sleep(self.sleep_time)

    def tfid_classify(self):

        tfidfconverter = TfidfVectorizer(max_features=1500, min_df=5, max_df=0.7, stop_words=stopwords.words('english'))
        X = tfidfconverter.fit_transform(self.data).toarray()

        clf = RandomForestClassifier(max_depth=100)
        clf.fit(X,self.headings)

        for i, item in enumerate(self.test["Text"]):
            print(item)
            print("--------------------------")
            print("Predicted: ", clf.predict(tfidfconverter.transform([item]).toarray()))
            print("Actual: ", self.test.iloc[i]["Heading"])
            print("--------------------------")
            time.sleep(self.sleep_time)

forest = ForestClassifier(data_dir, test_dir)
forest.preprocess_headings()
forest.preprocess_text()
forest.forest_classify()