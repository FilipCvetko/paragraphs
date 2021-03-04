import pandas as pd
from medwise_utils import get_headings
from config import *
import time
import nltk
import json
from tqdm import tqdm
from nltk.corpus import stopwords
nltk.download("punkt")
nltk.download("stopwords")

data = pd.read_csv("~/IT/DS/medwise/paragraphs/data/data.csv")

frequencies = dict()

for i in unique_master_headings:
	frequencies[i] = dict()

for i in tqdm(range(len(data))):
	master_headings = get_headings(data.iloc[i]["Heading"],master_only=True)
	text = data.iloc[i]["Text"]
	tokens = nltk.word_tokenize(text)
	for item in tokens:
		if item not in set(stopwords.words("english")):
			for heading in master_headings:
				if item not in frequencies[heading].keys():
					frequencies[heading][item] = 1
				else:
					frequencies[heading][item] += 1

for heading in frequencies.keys():
	frequencies[heading] = {k: v for k,v in sorted(frequencies[heading].items(), key=lambda item:item[1])}

with open("./reports/freqs.json", "w") as file:
	json.dump(frequencies, file, indent=4)
