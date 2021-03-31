import pandas as pd

file = "./../data/predicted2.csv"

df = pd.read_csv(file)
df = df.sample(frac=1)

for _, row in df.iterrows():
    print("----------------")
    print(row["text"])
    print(row["1"], row["2"], row["3"])
    print("----------------")
    input()