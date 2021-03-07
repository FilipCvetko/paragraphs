import pandas as pd
from medwise_utils import *
from config import *
import time
import nltk
import json
from tqdm import tqdm
from nltk.corpus import stopwords
nltk.download("punkt")
nltk.download("stopwords")

data = pd.read_csv("~/IT/DS/medwise/paragraphs/data/data.csv")

freqs = create_dict_from_text(unique_master_headings, data)
freqs, counts = count_words_per_heading(freqs)
print(counts)
write_dict_to_file(freqs, "/reports")