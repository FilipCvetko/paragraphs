import numpy as np
import pandas as pd
from sklearn import metrics
import transformers
import torch
import time
from torch.utils.data import Dataset, DataLoader, RandomSampler, SequentialSampler
from transformers import BertTokenizer, BertModel, BertConfig, AutoModel, AutoTokenizer
from tqdm import tqdm

# Preparing for TPU usage
# import torch_xla
# import torch_xla.core.xla_model as xm
# device = xm.xla_device()

# # Setting up the device for GPU usage

from torch import cuda
device = 'cuda' if cuda.is_available() else 'cpu'

data = pd.read_csv("./../data/predicted_bmj.csv")
data = data.sample(frac=1)

MAX_LEN = 512

tokenizer = AutoTokenizer.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext")

class BERTClass7(torch.nn.Module):
    def __init__(self):
        super(BERTClass7, self).__init__()
        self.l1 = AutoModel.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext")
        self.l2 = torch.nn.Dropout(0.3)
        self.l3 = torch.nn.Linear(768, 7)
    
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
        inputs = self.tokenizer.encode_plus(
            self.text,
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

data = data.reset_index(drop=True)

eval_params = {'batch_size': 1,
                'shuffle': True,
                'num_workers': 0
                }

model = BERTClass7()
model.load_state_dict(torch.load("./../models/microsoft.pth.tar", map_location=device))
model.eval()
model = model.to(device)

new_data_list = []

def evaluate():

    for ind, row in tqdm(data.iterrows()):
        row.reset_index(drop=True)
        if isinstance(row["text"], str):
            eval_set = CustomDataset(row["text"], tokenizer, MAX_LEN)
            eval_loader = DataLoader(eval_set, **eval_params)

            for new_data in eval_loader:

                ids = new_data['ids'].to(device, dtype = torch.long)
                mask = new_data['mask'].to(device, dtype = torch.long)
                token_type_ids = new_data['token_type_ids'].to(device, dtype = torch.long)


                outputs = model(ids, mask, token_type_ids)
                outputs = torch.sigmoid(outputs).cpu().detach().numpy().tolist()
                outputs = np.array(outputs) >= 0.5
               
                new_data_list.append({"title" : row["title"],
                                      "text" : row["text"], 
                                      "1" : row["1"], 
                                      "2" : row["2"],
                                      "3" : row["3"],
                                      "microsoft" : outputs})
                break

            # print("Text: ", row["text"])
            # print(data.loc[ind, "predicted"])

evaluate()

to_export = pd.DataFrame(new_data_list)
to_export.to_csv("./../data/predicted_bmj2.csv")