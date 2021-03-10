import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from medwise_utils import *
from nltk.corpus import stopwords
import nltk
from tqdm import tqdm
import time

# Load dataset
data = pd.read_csv("./data/data.csv")
data_list = data["Text"].tolist()

test = pd.read_csv("./data/test.csv")

headings_list = data["Heading"].tolist()
Y = []

for item in headings_list:
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

    Y.append(temp)

ps = PorterStemmer()

# for ind, val in tqdm(enumerate(data_list)):
#     tokens = nltk.word_tokenize(val)
#     new_tokens = []
    
#     for token in tokens:
#         if token not in set(stopwords.words("english")) and token.isalnum():
#             token = ps.stem(token)
#             new_tokens.append(token)

#     data_list[ind] = new_tokens

vectorizer = CountVectorizer(min_df=1)
X = vectorizer.fit_transform(data_list).toarray()

clf = RandomForestClassifier(max_depth=20)
clf.fit(X,Y)

for i, item in enumerate(test["Text"]):
    print(item)
    print("--------------------------")
    print("Predicted: ", clf.predict(vectorizer.transform([item]).toarray()))
    print("Actual: ", test.iloc[i]["Heading"])
    print("--------------------------")
    time.sleep(2)

