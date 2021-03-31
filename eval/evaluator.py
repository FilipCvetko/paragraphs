# -*- coding: utf-8 -*-
# Code for TPU packages install
# !curl -q https://raw.githubusercontent.com/pytorch/xla/master/contrib/scripts/env-setup.py -o pytorch-xla-env-setup.py
# !python pytorch-xla-env-setup.py --apt-packages libomp5 libopenblas-dev

# Importing stock ml libraries
import numpy as np
import pandas as pd
from sklearn import metrics
import transformers
import torch
import time
from torch.utils.data import Dataset, DataLoader, RandomSampler, SequentialSampler
from transformers import BertTokenizer, BertModel, BertConfig

# Preparing for TPU usage
# import torch_xla
# import torch_xla.core.xla_model as xm
# device = xm.xla_device()

# # Setting up the device for GPU usage

from torch import cuda
device = 'cuda' if cuda.is_available() else 'cpu'

"""<a id='section02'></a>
### Importing and Pre-Processing the domain data

We will be working with the data and preparing for fine tuning purposes. 
*Assuming that the `train.csv` is already downloaded, unzipped and saved in your `data` folder*

* Import the file in a dataframe and give it the headers as per the documentation.
* Taking the values of all the categories and coverting it into a list.
* The list is appened as a new column and other columns are removed
"""

# ALL DATA PREPROCESSING IS HERE.

data = pd.read_csv("./../data/title_text.csv")

# Defining some key variables that will be used later on in the training
MAX_LEN = 512

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Creating the customized model, by adding a drop out and a dense layer on top of distil bert to get the final output for the model. 

class BERTClass7(torch.nn.Module):
    def __init__(self):
        super(BERTClass7, self).__init__()
        self.l1 = transformers.BertModel.from_pretrained('bert-base-uncased')        
        self.l2 = torch.nn.Dropout(0.3)
        self.l3 = torch.nn.Linear(768, 7)
    
    def forward(self, ids, mask, token_type_ids):
        _, output_1= self.l1(ids, attention_mask = mask, token_type_ids = token_type_ids)
        output_2 = self.l2(output_1)
        output = self.l3(output_2)
        return output

# Creating the customized model, by adding a drop out and a dense layer on top of distil bert to get the final output for the model. 

class BERTClass6(torch.nn.Module):
    def __init__(self):
        super(BERTClass6, self).__init__()
        self.l1 = transformers.BertModel.from_pretrained('bert-base-uncased')        
        self.l2 = torch.nn.Dropout(0.3)
        self.l3 = torch.nn.Linear(768, 6)
    
    def forward(self, ids, mask, token_type_ids):
        _, output_1= self.l1(ids, attention_mask = mask, token_type_ids = token_type_ids)
        output_2 = self.l2(output_1)
        output = self.l3(output_2)
        return output

class CustomDataset(Dataset):

    def __init__(self, text, tokenizer, max_len):
        self.tokenizer = tokenizer
        self.text = text
        self.max_len = max_len

    def __len__(self):
        return len(self.text)

    def __getitem__(self, index):
        text = str(self.text[index])
        text = " ".join(text.split())

        inputs = self.tokenizer.encode_plus(
            text,
            None,
            add_special_tokens=True,
            max_length=self.max_len,
            pad_to_max_length=True,
            return_token_type_ids=True,
            truncation = True
        )
        ids = inputs['input_ids']
        mask = inputs['attention_mask']
        token_type_ids = inputs["token_type_ids"]


        return {
            'ids': torch.tensor(ids, dtype=torch.long),
            'mask': torch.tensor(mask, dtype=torch.long),
            'token_type_ids': torch.tensor(token_type_ids, dtype=torch.long),
        }

# Creating the dataset and dataloader for the neural network

data = data.reset_index(drop=True)

eval_params = {'batch_size': 1,
                'shuffle': True,
                'num_workers': 0
                }

data["predicted"] = np.nan

device = torch.device('cpu')

model_one = BERTClass6()
model_one.load_state_dict(torch.load("./../models/BERTforSeqClassification.pth.tar", map_location=device))
model_one.eval()
model_one = model_one.to(device)

# model_two = BERTClass7()
# model_two.load_state_dict(torch.load("./../models/medications_separate.pth.tar", map_location=device))
# model_two.eval()
# model_two = model_two.to(device)

# model_three = BERTClass7()
# model_three.load_state_dict(torch.load("./../models/referrals_added.pth.tar", map_location=device))
# model_three.eval()
# model_three = model_three.to(device)

def evaluate():
    for ind, row in data.iterrows():
        row.reset_index(drop=True)
        eval_set = CustomDataset(row["text"], tokenizer, MAX_LEN)

        eval_loader = DataLoader(eval_set, **eval_params)

        for new_data in eval_loader:

            ids = new_data['ids'].to(device, dtype = torch.long)
            mask = new_data['mask'].to(device, dtype = torch.long)
            token_type_ids = new_data['token_type_ids'].to(device, dtype = torch.long)


            outputs_one = model_one(ids, mask, token_type_ids)
            print(ids[:10])
            # outputs_two = model_two(ids, mask, token_type_ids)
            # outputs_three = model_three(ids, mask, token_type_ids)
            outputs_one = torch.sigmoid(outputs_one).cpu().detach().numpy().tolist()
            # outputs_two = torch.sigmoid(outputs_two).cpu().detach().numpy().tolist()
            # outputs_three = torch.sigmoid(outputs_three).cpu().detach().numpy().tolist()

            outputs_one = np.array(outputs_one) >= 0.5
            print(outputs_one)
            # outputs_two = np.array(outputs_two) >= 0.5
            # outputs_three = np.array(outputs_three) >= 0.5

            data.loc[ind, "predicted"] = str(outputs_one)
            # data.loc[ind, "two"] = str(outputs_two)
            # data.loc[ind, "three"] = str(outputs_three)
            print("before break")
            break

        print("Text: ", row["text"])
        print(data.loc[ind, "predicted"])

evaluate()

data.to_csv("./predicted1.csv")