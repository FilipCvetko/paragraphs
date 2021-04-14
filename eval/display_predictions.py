import pandas as pd

file = "./../data/predicted_nicecks2.csv"

df = pd.read_csv(file)
df = df.sample(frac=1)

for _, row in df.iterrows():
    print("----------------")
    print(row["title"])
    print(row["text"])
    print(row["1"])
    print(row["2"])
    print(row["3"])
    print(row["microsoft"])
    print("----------------")
    input()