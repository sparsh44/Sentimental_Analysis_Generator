from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
import json
import csv
import ssl
import nltk
import spacy
import torch
import threading
import numpy as np
import pandas as pd
import contractions
import urllib.request
from scipy.special import softmax
from urllib.request import urlopen
from keras.models import load_model
from django.http import JsonResponse
from nltk.tokenize import ToktokTokenizer
from deep_translator import GoogleTranslator
from keras.preprocessing.sequence import pad_sequences
from transformers import DistilBertTokenizer
from keras.preprocessing.sequence import pad_sequences
import numpy as np
from transformers import AutoModelForSequenceClassification
from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer
import numpy as np
from scipy.special import softmax
import csv
import urllib.request
import pandas as pd
import torch
from crawlers.AajTak import AajTak
from crawlers.AajTakVideo import Aajtak_Video
from crawlers.IndiaToday import IndiaToday
from crawlers.IndiaToday_Chandigarh import IndiaToday_Chandigarh
from crawlers.JagranChandigarh import JagranChandigarh
from crawlers.News18 import News18
from crawlers.News18Punj import News18Punj
from crawlers.IndianExpressVideo import IndianExpressVideo
from crawlers.IndiaTv import IndiaTv
import urllib.request
from urllib.request import urlopen
import ssl
import json
ssl._create_default_https_context = ssl._create_unverified_context


# mapping_link = f"https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/sentiment/mapping.txt"
# with urllib.request.urlopen(mapping_link,timeout=120) as f:
#     html = f.read().decode('utf-8').split("\n")
#     csvreader = csv.reader(html, delimiter='\t')
mapping_file_path = "mapping.txt"

with open(mapping_file_path, 'r', encoding='utf-8') as file:
    csvreader = csv.reader(file, delimiter='\t')
    labels = [row[1] for row in csvreader if len(row)>1]

tokenizer_auto = AutoTokenizer.from_pretrained("tokenizer_roberta/sentiment_tokenizer/")
model_auto = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment/")


def sentiment(row):
    labels=[]
    text = row[:1500]
    encoded_input = tokenizer_auto(text, return_tensors='pt') 
    with torch.no_grad():  
        output = model_auto(**encoded_input)
    scores = output.logits[0]  
    scores = torch.softmax(scores, dim=0)

    ranking = torch.argsort(scores, descending=True)
    max_score = 0
    ans=[0,0,0]
    for i in range(scores.shape[0]):
        l = labels[ranking[i].item()]
        s = scores[ranking[i]].item()
        if(l=="neutral"):
            ans[2]=s
        elif(l=="negative"):
            ans[1]=s
        else:
            ans[0]=s

    return ans[:]


custom_objects = {'TFDistilBertModel': TFDistilBertModel}

loaded_model = load_model("distilbert_model.h5", custom_objects=custom_objects)
categories = {
0:"Entertainment",
1:"Business" ,
2:"Politics" ,
3:"Judiciary" ,
4:"Crime"  ,
5:"Culture" ,
6:"Sports" ,
7:"Science"  ,
8:"International" ,
9:"Technology" 
}


tokenizer_bert = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
print("tokenizer ready")
def predict_text(loaded_model, text):
    max_length = 512
    inputs = tokenizer_bert(text, return_tensors='tf', truncation=True, padding='max_length', max_length=max_length)
    input_ids = inputs['input_ids']
    attention_mask = inputs['attention_mask']
    predictions = loaded_model.predict([input_ids, attention_mask])
    return predictions


def classification(row):
    example_text = row
    predictions = predict_text(loaded_model, example_text)
    value_to_find = predictions[0].argmax()
    predicted_class = categories[value_to_find]
    return predicted_class


def preprocess(series):
    series = series.apply(lambda x: str(x).lower())
    def remove_contractions(row):
        return contractions.fix(row)
    series = series.apply(lambda x: remove_contractions(x))
    series = series.str.replace(r'[^\w\s]', '', regex=True)
    series = series.str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
    
    def remove_numbers(text):
        pattern = r'[^a-zA-z.,!?/:;\"\'\s]' 
        return re.sub(pattern, '', text)
    series = series.apply(lambda x: remove_numbers(x))
    
    nlp = spacy.load('en_core_web_sm')
    def get_lem(text):
        text = nlp(text)
        text = ' '.join([word.lemma_ if word.lemma_ != '-PRON-' else word.text for word in text])
        return text
    series = series.apply(lambda x: get_lem(x))
    
    tokenizer = ToktokTokenizer()
    stopword_list = nltk.corpus.stopwords.words('english')
    stopword_list.remove('not')
    def remove_stopwords(text):
        tokens = tokenizer.tokenize(text)
        tokens = [token.strip() for token in tokens]
        t = [token for token in tokens if token.lower() not in stopword_list]
        text = ' '.join(t)    
        return text
    series = series.apply(lambda x: remove_stopwords(x))
    return series


def translate(row):
        try:
            if(len(row)>0):
                result=GoogleTranslator(source='auto', target='en').translate(row[:2200])
                return result
            else:
                return row
        except:
            return ""
        

def PreProcessTheData():
    # India Today
    df = pd.read_excel("IndiaToday.xlsx")
    def remove_edited(row):
        try:
            index_of_edited_by = row.find("Edited By: ")

            if index_of_edited_by != -1:
                modified_text = row[:index_of_edited_by]
                return modified_text
            else:
                return row
        except:
            return ""
    df.Body = df.Body.apply(lambda x: remove_edited(x)) 
    df = df[~df['Body'].apply(lambda x: isinstance(x, (float, int)))]
    df = df[~df['Heading'].str.contains('horoscope', case=False)]
    df.Body = preprocess(df.Body)
    df = df.dropna()

    # AajTak Video 
    df2 = pd.read_excel("AajTak_Video.xlsx")
    df2.Body=df2.Body.apply(lambda x: translate(x))
    df2.drop('VideoText', axis=1, inplace=True)
    df2 = df2[~df2['Body'].apply(lambda x: isinstance(x, (float, int)))]
    df2 = df2.loc[~(df2['Heading'].str.contains("Aaj Ki Baat") | df2['Heading'].str.contains("Horoscope")
                | df2['Heading'].str.contains("Aap Ki Adalat"))]
    df2 = df2[~df2['Heading'].str.contains('horoscope', case=False)]
    df2.Body = preprocess(df2.Body)
    df2 = df2.dropna()

    # Indian Express Video
    df3 = pd.read_excel("IndianExpress_Video.xlsx")
    df3.Body=df3.Body.apply(lambda x: translate(x))
    df3.drop('VideoText', axis=1, inplace=True)
    df3 = df3[~df3['Body'].apply(lambda x: isinstance(x, (float, int)))]
    df3 = df3[~df3['Heading'].str.contains('horoscope', case=False)]
    df3.Body = preprocess(df3.Body)
    df3 = df3.dropna()
    
    # Jagran Punjab
    df4 = pd.read_excel("Jagran_Punjab.xlsx")
    df4 = df4[~df4['Body'].apply(lambda x: isinstance(x, (float, int)))]
    df4.Body = preprocess(df4.Body)
    def remove_punjab_event(row):
        try:
            index_of_edited_by = row.find("punjab event directly impact life")

            if index_of_edited_by != -1:
                modified_text = row[index_of_edited_by+34:]
                return modified_text
            else:
                return row
        except:
            return ""
    df4.Body = df4.Body.apply(lambda x: remove_punjab_event(x))
    df4 = df4.dropna()

    # News18 Punjab
    df5 = pd.read_excel("News18_Punjab.xlsx")
    df5 = df5[~df5['Body'].apply(lambda x: isinstance(x, (float, int)))]
    df5 = df5[~(df5['Body'].str.contains('dear subscriber', case=False))]
    df5 = df5[~df5['Heading'].str.contains('horoscope', case=False)]
    df5.Body = preprocess(df5.Body)
    df5 = df5.dropna()

    # AajTak
    df6 = pd.read_excel("AajTak.xlsx")
    df6 = df6[~df6['Body'].apply(lambda x: isinstance(x, (float, int)))]
    df6 = df6[~(df6['Body'].str.contains('dear subscriber', case=False))]
    df6 = df6[~df6['Heading'].str.contains('horoscope', case=False)]
    df6.Body = preprocess(df6.Body)
    df6 = df6.dropna()

    # India Today Chandigarh
    df7 = pd.read_excel("IndiaToday_Chandigarh.xlsx")
    df7 = df7[~df7['Body'].apply(lambda x: isinstance(x, (float, int)))]
    def remove_also_read(row):
        try:
            index_of_edited_by = row.find("ALSO READ")

            if index_of_edited_by != -1:
                modified_text = row[:index_of_edited_by]
                return modified_text
            else:
                return row
        except:
            return ""
    df7.Body = df7.Body.apply(lambda x: remove_also_read(x)) 
    df7.Body = preprocess(df.Body)
    df7.dropna(inplace=True)

    df8 = pd.concat([df, df2, df3, df4, df5, df6, df7], ignore_index=True, axis=0, join='outer')
    df8["Cat"]=df8["Body"].apply(lambda x:classification(str(x)))
    df8["Sentiment"] = df8.Body.apply(lambda x: sentiment(str(x)))

    file_name = "Final_Prepped_Data.xlsx"
    df8.to_excel(file_name, index=False)
    
    
def index (request):
    print("The Session started")
    # thread1 = threading.Thread(target=AajtakVideo)
    # thread2 = threading.Thread(target=IndiaToday)
    thread3 = threading.Thread(target=IndiaToday_Chandigarh)
    # thread4=threading.Thread(target=News18)
    # thread7=threading.Thread(target=News18Punj)
    # thread8=threading.Thread(target=IndiaTv)
    # thread9=threading.Thread(target=JagranChandigarh)
    # thread10=threading.Thread(target=AajTak)

    # Start the threads
    # thread1.start()
    # thread2.start()
    thread3.start()
    # thread4.start()
    # thread7.start()
    # thread8.start()
    # thread9.start()
    # thread10.start()
   

    # Wait for all threads to finish
    # thread1.join()
    # thread2.join()
    thread3.join()
    # thread4.join()
    # thread7.join()
    # thread8.join()
    # thread9.join()
    # thread10.join()
    print("Done")

    PreProcessTheData()
    news=[]
    df=pd.read_excel("Final_Prepped_Data.xlsx")
    for ind in df.index:
        row={}
        row["Title"]=df["Heading"][ind]
        row["Description"]=df["Body"][ind]
        row["URL"]=df["URL"][ind]
        row["Categories"]=df["Cat"][ind]
        row["Sentiment_Score"]=df["Sentiment"][ind]
        news.append(row)
        
    print("PreProcessing Done")
    print("Session Ended")
    

    return JsonResponse({"result":"success", "News":news}, safe=False, json_dumps_params={'ensure_ascii': False})

