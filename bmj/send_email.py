from_email = "automatedresponse9@gmail.com"
server = "smtp.gmail.com"
port = 465
password = "aimlresearch"
to_email1 = "neza.bogataj9@gmail.com"
to_email2 = "filipcvetko123@gmail.com"


import smtplib
from email.message import EmailMessage
import random
import pandas as pd

df = pd.read_csv("./../data/cases.csv")
df.sample(frac=1)

ind = random.randint(0,len(df)-1)

def send_case(receiver):

    subject = "Klinični primer"
    text = df.loc[ind, "case"] + "\n"*40 + df.loc[ind, "disease"]
    print(text)
    msg = EmailMessage()
    msg.set_content(text)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = receiver

    return msg


server = smtplib.SMTP_SSL(server,port)
server.login(from_email, password)
server.send_message(send_case(to_email1))
server.send_message(send_case(to_email2))
server.quit()