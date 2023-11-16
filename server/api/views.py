from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
import json
import csv
import requests
from bs4 import BeautifulSoup
import subprocess
from api import Aajtak_Video
from api import IndianExpress_Video
from api import ZeeNews_Video
import threading
import time
import xlsxwriter
import pandas as pd
import contractions
import re
import nltk
from nltk.tokenize import ToktokTokenizer
import spacy
import nltk
from deep_translator import GoogleTranslator
from keras.models import load_model
from transformers import TFDistilBertModel
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

import urllib.request
from urllib.request import urlopen
import ssl
import json
ssl._create_default_https_context = ssl._create_unverified_context


tokenizer = AutoTokenizer.from_pretrained("tokenizer_roberta/sentiment_tokenizer/")
model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment/")
labels=[]
# mapping_link = f"https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/sentiment/mapping.txt"
# with urllib.request.urlopen(mapping_link,timeout=120) as f:
#     html = f.read().decode('utf-8').split("\n")
#     csvreader = csv.reader(html, delimiter='\t')
mapping_file_path = "mapping.txt"

with open(mapping_file_path, 'r', encoding='utf-8') as file:
    csvreader = csv.reader(file, delimiter='\t')
    labels = [row[1] for row in csvreader if len(row)>1]

def sentiment(row):
    text = row[:1500]
    encoded_input = tokenizer(text, return_tensors='pt') 
    with torch.no_grad():  
        output = model(**encoded_input)
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
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
print("tokenizer ready")
max_length = 512

def predict_text(loaded_model, text):

    inputs = tokenizer(text, return_tensors='tf', truncation=True, padding='max_length', max_length=max_length)
    

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

def PreProcessTheData():
    def translate(row):
        try:
            if(len(row)>0):
                result=GoogleTranslator(source='auto', target='en').translate(row[:2200])
                return result
            else:
                return row
        except:
            return ""
        
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

    df2 = pd.read_excel("AajTak_Video.xlsx")
    df2.Body=df2.Body.apply(lambda x: translate(x))
    df2.drop('VideoText', axis=1, inplace=True)
    df2 = df2[~df2['Body'].apply(lambda x: isinstance(x, (float, int)))]
    df2 = df2.loc[~(df2['Heading'].str.contains("Aaj Ki Baat") | df2['Heading'].str.contains("Horoscope")
                | df2['Heading'].str.contains("Aap Ki Adalat"))]
    df2 = df2[~df2['Heading'].str.contains('horoscope', case=False)]
    df2.Body = preprocess(df2.Body)
    df2 = df2.dropna()

    df3 = pd.read_excel("IndianExpress_Video.xlsx")
    df3.Body=df3.Body.apply(lambda x: translate(x))
    df3.drop('VideoText', axis=1, inplace=True)
    df3 = df3[~df3['Body'].apply(lambda x: isinstance(x, (float, int)))]
    df3 = df3[~df3['Heading'].str.contains('horoscope', case=False)]
    df3.Body = preprocess(df3.Body)
    df3 = df3.dropna()
    
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

    df5 = pd.read_excel("News18_Punjab.xlsx")
    df5 = df5[~df5['Body'].apply(lambda x: isinstance(x, (float, int)))]
    df5 = df5[~(df5['Body'].str.contains('dear subscriber', case=False))]
    df5 = df5[~df5['Heading'].str.contains('horoscope', case=False)]
    df5.Body = preprocess(df5.Body)
    df5 = df5.dropna()

    df6 = pd.read_excel("AajTak.xlsx")
    df6 = df6[~df6['Body'].apply(lambda x: isinstance(x, (float, int)))]
    df6 = df6[~(df6['Body'].str.contains('dear subscriber', case=False))]
    df6 = df6[~df6['Heading'].str.contains('horoscope', case=False)]
    df6.Body = preprocess(df6.Body)
    df6 = df6.dropna()

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
    
       

def News18():
    print("News 18")
    workbook=xlsxwriter.Workbook('News18.xlsx')
    worksheet=workbook.add_worksheet()
    row=0
    column=0
    worksheet.write(row,column,"Heading")
    worksheet.write(row,column+1,"Body")
    worksheet.write(row,column+2,"Category")
    worksheet.write(row,column+3,"URL")
    row+=1
    HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
    r=requests.get('https://www.news18.com', headers=HEADERS)
    urls_to_visit=[]
    unique_urls={}
    count=0
    try:
        if(r.status_code==200):
            soup=BeautifulSoup(r.text, 'html.parser')
        
            for url in soup.findAll('a'):
                try:
                    if(url.has_attr('href')):
                        if("video" not in url['href'].split("/") and "tag" not in url['href'].split("/") and "author" not in url['href'].split("/")):
                            if(url['href'][0]=='/' and "https://www.news18.com"+url['href'] not in unique_urls.keys()):
                                unique_urls["https://www.news18.com"+url['href']]=True
                                urls_to_visit.append("https://www.news18.com"+url['href'])
                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.news18.com" and url['href'] not in unique_urls.keys()):
                                unique_urls[url['href']]=True
                                urls_to_visit.append(url['href'])
                finally:
                    continue


        while(urls_to_visit and count<20):
                urltoVisit=urls_to_visit[0]
                print(count)
                print(urltoVisit)
                urls_to_visit.pop(0)
                if(urltoVisit[0]=='h' and (["tags","tag", "livetv", "videos", "web-stories", "astrology"] not in urltoVisit.split("/"))):
                    try:
                        
                        r=requests.get(urltoVisit, headers=HEADERS)
                        if(r.status_code==200):
                            soup=BeautifulSoup(r.text, 'html.parser')
                            for url in soup.findAll('a'):
                                try:
                                    if(url.has_attr('href')):
                                        if("video" not in url['href'].split("/") and "tag" not in url['href'].split("/") and "author" not in url['href'].split("/")):
                                            if(url['href'][0]=='/' and "https://www.news18.com"+url['href'] not in unique_urls.keys()):
                                                unique_urls["https://www.news18.com"+url['href']]=True
                                                urls_to_visit.append("https://www.news18.com"+url['href'])
                                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.news18.com" and url['href'] not in unique_urls.keys()):
                                                unique_urls[url['href']]=True
                                                urls_to_visit.append(url['href'])
                                finally:
                                    continue
                            
                            if(soup.find('h1', {'class':'article_heading1'}) and (soup.find('html',{'lang':'en'}) or soup.find('html',{'lang':'en-us'})or soup.find('html',{'lang':'en-uk'}))):
                                heading_title=soup.find('h1', {'class':'article_heading1'})
                                
                        
                                
                                if(soup.find('div', {'id':'article_ContentWrap'}).findAll('p')):
                                
                                    
                                    heading_desc=soup.find('div', {'id':'article_ContentWrap'}).findAll('p')
                                    news=""
                                    for text in heading_desc:
                                        news+=text.text
                                    worksheet.write(row,column,heading_title.text)
                                    worksheet.write(row,column+1,news)
                                    worksheet.write(row,column+2,urltoVisit.split("/")[3])
                                    worksheet.write(row,column+3,urltoVisit)
                                
                                    row+=1
                                    
                                    count+=1
                    finally:
                        continue        
            
    finally:
        print("News18 Finished")
        workbook.close()
        
      
        
        
def IndiaTv():
    print("India Tv")
    workbook=xlsxwriter.Workbook('IndiaTv.xlsx')
    worksheet=workbook.add_worksheet()
    row=0
    column=0
    worksheet.write(row,column,"Heading")
    worksheet.write(row,column+1,"Body")
    worksheet.write(row,column+2,"Category")
    worksheet.write(row,column+3,"URL")
    row+=1
    HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
    r=requests.get('https://www.indiatvnews.com', headers=HEADERS)
    urls_to_visit=[]
    unique_urls={}
    count=0
    try:
        if(r.status_code==200):
            soup=BeautifulSoup(r.text, 'html.parser')
            for url in soup.findAll('a'):
                try:
                    if(url.has_attr('href')):
                        if("video" not in url['href'].split("/") and "tag" not in url['href'].split("/") and "author" not in url['href'].split("/")):
                            if(url['href'][0]=='/' and "https://www.indiatvnews.com"+url['href'] not in unique_urls.keys()):
                                unique_urls["https://www.indiatvnews.com"+url['href']]=True
                                urls_to_visit.append("https://www.indiatvnews.com"+url['href'])
                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.indiatvnews.com" and url['href'] not in unique_urls.keys()):
                                unique_urls[url['href']]=True
                                urls_to_visit.append(url['href'])
                finally:
                    continue
        while(urls_to_visit and count<20):
                urltoVisit=urls_to_visit[0]
                
                urls_to_visit.pop(0)
                if(urltoVisit[0]=='h' and (["tags","tag", "livetv?utm_source=mobiletophead&amp;utm_campaign=livetvlink", "video", "news-podcasts", "lifestyle","astrology", "web-stories"] not in urltoVisit.split("/"))):
                    try:
                        r=requests.get(urltoVisit, headers=HEADERS)
                        if(r.status_code==200):
                            soup=BeautifulSoup(r.text, 'html.parser')
                            for url in soup.findAll('a'):
                                try:
                                    if(url.has_attr('href')):
                                        if("video" not in url['href'].split("/") and "tag" not in url['href'].split("/") and "author" not in url['href'].split("/")):
                                            if(url['href'][0]=='/' and "https://www.indiatvnews.com"+url['href'] not in unique_urls.keys()):
                                                unique_urls["https://www.indiatvnews.com"+url['href']]=True
                                                urls_to_visit.append("https://www.indiatvnews.com"+url['href'])
                                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.indiatvnews.com" and url['href'] not in unique_urls.keys()):
                                                unique_urls[url['href']]=True
                                                urls_to_visit.append(url['href'])
                                finally:
                                    continue
                            
                            if(soup.find('div', {'class':'article-title'}) and (soup.find('html',{'lang':'en'}) or soup.find('html',{'lang':'en-us'})or soup.find('html',{'lang':'en-uk'})) ):
                                heading_title=soup.find('div', {'class':'article-title'}).find('h1')
                                
                                if(soup.find('div', {'id':'content'}).findAll('p')):
                               
                                    heading_desc=soup.find('div', {'id':'content'}).findAll('p')
                                    news=""
                                    for i in range(len(heading_desc)-4):
                                       
                                        news+=heading_desc[i].text
                                    worksheet.write(row,column,heading_title.text)
                                    worksheet.write(row,column+1,news)
                                    if(urltoVisit.split("/")[3]!='news'):
                                        worksheet.write(row,column+2,urltoVisit.split("/")[4])
                                    else:
                                        worksheet.write(row,column+2,urltoVisit.split("/")[3])
                                    worksheet.write(row,column+3,urltoVisit)
                              
                                    row+=1
                                    
                                    count+=1
                    finally:
                        continue        
            
        
    finally:
        print("IndiaTv finished")
        workbook.close()     

def IndiaToday():
    print("India Today")
    workbook=xlsxwriter.Workbook('IndiaToday.xlsx')
    worksheet=workbook.add_worksheet()
    row=0
    column=0
    worksheet.write(row,column,"Heading")
    worksheet.write(row,column+1,"Body")
    worksheet.write(row,column+2,"Category")
    worksheet.write(row,column+3,"URL")
    row+=1
    HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
    r=requests.get('https://www.indiatoday.in', headers=HEADERS)
    urls_to_visit=[]
    unique_urls={}
    count=0
    try:
        if(r.status_code==200):
            soup=BeautifulSoup(r.text, 'html.parser')
            for url in soup.findAll('a'):
                try:
                    if(url.has_attr('href')):
                        if("video" not in url['href'].split("/") and "tag" not in url['href'].split("/") and "author" not in url['href'].split("/")):
                            if(url['href'][0]=='/' and "https://www.indiatoday.in"+url['href'] not in unique_urls.keys()):
                                unique_urls["https://www.indiatoday.in"+url['href']]=True
                                urls_to_visit.append("https://www.indiatoday.in"+url['href'])
                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.indiatoday.in" and url['href'] not in unique_urls.keys()):
                                unique_urls[url['href']]=True
                                urls_to_visit.append(url['href'])
                finally:
                    continue
        while(urls_to_visit and count<20):
                urltoVisit=urls_to_visit[0]
                urls_to_visit.pop(0)
           
                if(urltoVisit[0]=='h' and (["tags","tag", "livetv", "video"] not in urltoVisit.split("/"))):
                    try:
                        r=requests.get(urltoVisit, headers=HEADERS)
                        if(r.status_code==200):
                            soup=BeautifulSoup(r.text, 'html.parser')
                            for url in soup.findAll('a'):
                                try:
                                    if(url.has_attr('href')):
                                        if("video" not in url['href'].split("/") and "tag" not in url['href'].split("/") and "author" not in url['href'].split("/")):
                                            if(url['href'][0]=='/' and "https://www.indiatoday.in"+url['href'] not in unique_urls.keys()):
                                                unique_urls["https://www.indiatoday.in"+url['href']]=True
                                                urls_to_visit.append("https://www.indiatoday.in"+url['href'])
                                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.indiatoday.in" and url['href'] not in unique_urls.keys()):
                                                unique_urls[url['href']]=True
                                                urls_to_visit.append(url['href'])
                                finally:
                                    continue
                            
                            if(soup.find('div', {'class':'jsx-99cc083358cc2e2d Story_story__content__body__qCd5E story__content__body widgetgap'}) and (soup.find('html',{'lang':'en'}) or soup.find('html',{'lang':'en-us'})or soup.find('html',{'lang':'en-uk'}))):
                                heading_title=soup.find('div', {'class':'jsx-99cc083358cc2e2d Story_story__content__body__qCd5E story__content__body widgetgap'}).find('h1')
                                if(soup.find('div', {'class':'jsx-99cc083358cc2e2d Story_description__fq_4S description'}).findAll('p')):
                            
                                    
                                    
                                    heading_desc=soup.find('div', {'class':'jsx-99cc083358cc2e2d Story_description__fq_4S description'}).findAll('p')
                                    news=""
                                    for text in heading_desc:
                                        
                                        news+=text.text
                        
                                    worksheet.write(row,column,heading_title.text)
                                    worksheet.write(row,column+1,news)
                                    if(urltoVisit.split("/")[3]!='cities'):
                                        worksheet.write(row,column+2,urltoVisit.split("/")[3])
                                    else:
                                        worksheet.write(row,column+2,"india")
                                    worksheet.write(row,column+3,urltoVisit)
                              
                                    row+=1
                                    
                                    count+=1
                    finally:
                        continue        
            
        
    finally:
        print("India today finished")
        workbook.close()
    

def News18Punj():
    print("New 18 Punjab")
    workbook=xlsxwriter.Workbook('News18_Punjab.xlsx')
    worksheet=workbook.add_worksheet()
    row=0
    column=0
    worksheet.write(row,column,"Heading")
    worksheet.write(row,column+1,"Body")
    worksheet.write(row,column+2,"Category")
    worksheet.write(row,column+3,"URL")
    row+=1
    HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
    r=requests.get('https://punjab.news18.com', headers=HEADERS)
    urls_to_visit=[]
    unique_urls={}
    count=0
    try:
        
        if(r.status_code==200):
            r.encoding = 'utf-8'
            soup=BeautifulSoup(r.text, 'html.parser')
        
            for url in soup.findAll('a'):
                try:
                    if(url.has_attr('href')):
                        if("video" not in url['href'].split("/") and "tag" not in url['href'].split("/") and "author" not in url['href'].split("/")):
                        
                            if(url['href'][0]=='/' and "https://punjab.news18.com"+url['href'] not in unique_urls.keys()):
                                unique_urls["https://punjab.news18.com"+url['href']]=True
                                urls_to_visit.append("https://punjab.news18.com"+url['href'])
                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="punjab.news18.com" and url['href'] not in unique_urls.keys()):
                                unique_urls[url['href']]=True
                                urls_to_visit.append(url['href'])
                finally:
                    continue


        while(urls_to_visit and count<20):
                urltoVisit=urls_to_visit[0]
                
                urls_to_visit.pop(0)
                print(count)
                print(urltoVisit)
                if(urltoVisit[0]=='h' and (["tags","tag", "livetv", "videos", "web-stories", "astrology"] not in urltoVisit.split("/"))):
                    try:
                        
                        r=requests.get(urltoVisit, headers=HEADERS)
                        r.encoding = 'utf-8'
                        if(r.status_code==200):
                            soup=BeautifulSoup(r.text, 'html.parser')
                            for url in soup.findAll('a'):
                                try:
                                    if(url.has_attr('href')):
                                        if("video" not in url['href'].split("/") and "tag" not in url['href'].split("/") and "author" not in url['href'].split("/")):
                                            if(url['href'][0]=='/' and "https://punjab.news18.com"+url['href'] not in unique_urls.keys()):
                                                unique_urls["https://punjab.news18.com"+url['href']]=True
                                                urls_to_visit.append("https://punjab.news18.com"+url['href'])
                                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="punjab.news18.com" and url['href'] not in unique_urls.keys()):
                                                unique_urls[url['href']]=True
                                                urls_to_visit.append(url['href'])
                                finally:
                                    continue
                            
                            if(soup.find('h1', { 'class':"tphd"}) and (soup.find('html',{'lang':'pa'}))):
                                
                                heading_title=soup.find('h1', { 'class':"tphd"})
                                heading_title=heading_title.text
                                print(heading_title)
                                if(soup.find('div', {'id':'main-content'}).findAll('p')):
                                    
                                
                                    heading_desc=soup.find('div', {'id':'main-content'}).findAll('p')
                                    print("yes")
                                    news=""
                                    for text in heading_desc:
                                
                                        news+=text.text
                                    news=news.replace("\xa0","")
                                    news=news.replace("\n","")
                                    heading_title=heading_title.replace("\xa0","")
                                    heading_title=heading_title.replace("\n","")
                                    result=GoogleTranslator(source='auto', target='en').translate(news[0:2200])
                                    headline=GoogleTranslator(source='auto', target='en').translate(heading_title)
                                    print(result)
                                    print(headline)
                                    
                                    worksheet.write(row,column,headline)
                                    worksheet.write(row,column+1,result)
                                    worksheet.write(row,column+2,urltoVisit.split("/")[3])
                                    worksheet.write(row,column+3,urltoVisit)
                                
                                    row+=1
                                
                                    count+=1
                    finally:
                        continue        
            
        
    finally:
        print("Punjabi Done")
        workbook.close()
        
def AajTak():
    print("AajTak")
    workbook=xlsxwriter.Workbook('AajTak.xlsx')
    worksheet=workbook.add_worksheet()
    row=0
    column=0
    worksheet.write(row,column,"Heading")
    worksheet.write(row,column+1,"Body")
    worksheet.write(row,column+2,"Category")
    worksheet.write(row,column+3,"URL")
    row+=1
    HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
    r=requests.get('https://www.aajtak.in', headers=HEADERS)
    urls_to_visit=[]
    unique_urls={}
    count=0
    try:
        if(r.status_code==200):
            soup=BeautifulSoup(r.text, 'html.parser')
           
            for url in soup.findAll('a'):
                try:
                    if(url.has_attr('href')):
                        if("video" not in url['href'].split("/") and "tag" not in url['href'].split("/") and "author" not in url['href'].split("/")):
                           
                            if(url['href'][0]=='/' and "https://www.aajtak.in"+url['href'] not in unique_urls.keys()):
                                unique_urls["https://www.aajtak.in"+url['href']]=True
                                urls_to_visit.append("https://www.aajtak.in"+url['href'])
                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.aajtak.in" and url['href'] not in unique_urls.keys()):
                                unique_urls[url['href']]=True
                                urls_to_visit.append(url['href'])
                finally:
                    continue
        while(urls_to_visit and count<20):
                urltoVisit=urls_to_visit[0]
                
                urls_to_visit.pop(0)
                if(urltoVisit[0]=='h' and (["tags","tag", "livetv?utm_source=homepage&utm_campaign=hp_topicon", "video", "news-podcasts", "lifestyle","astrology","visualstories"] not in urltoVisit.split("/"))):
                    try:
                        r=requests.get(urltoVisit, headers=HEADERS)
                        if(r.status_code==200):
                            soup=BeautifulSoup(r.text, 'html.parser')
                            for url in soup.findAll('a'):
                                try:
                                    if(url.has_attr('href')):
                                        if(url['href'][0]=='/' and "https://www.aajtak.in"+url['href'] not in unique_urls.keys()):
                                            unique_urls["https://www.aajtak.in"+url['href']]=True
                                            urls_to_visit.append("https://www.aajtak.in"+url['href'])
                                        elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.aajtak.in" and url['href'] not in unique_urls.keys()):
                                            unique_urls[url['href']]=True
                                            urls_to_visit.append(url['href'])
                                finally:
                                    continue
                            
                            if(soup.find('div', {'class':'story-heading'}) and (soup.find('html',{'lang':'hi'}))):
                                heading_title=soup.find('div', {'class':'story-heading'}).find('h1')
                                heading_title=heading_title.text
                                if(soup.find('div', {'class':'story-with-main-sec'}).findAll('p')):
                                
                                    heading_desc=soup.find('div', {'class':'story-with-main-sec'}).findAll('p')
                                    news=""
                                    for i in range(len(heading_desc)-4):
                             
                                        news+=heading_desc[i].text
                                    news=news.replace("\xa0","")
                                    news=news.replace("\n","")
                                    heading_title=heading_title.replace("\xa0","")
                                    heading_title=heading_title.replace("\n","")
                                    
                                    result=GoogleTranslator(source='auto', target='en').translate(news[0:2200])
                                    headline=GoogleTranslator(source='auto', target='en').translate(heading_title)
                                    
                                    worksheet.write(row,column,headline)
                                    worksheet.write(row,column+1,result)
                                    worksheet.write(row,column+2,urltoVisit.split("/")[3])
                                    worksheet.write(row,column+3,urltoVisit)
                                    row+=1
                                    count+=1
                    finally:
                        continue        
            
        
    finally:
        print("Aaj Tak Ended")
        workbook.close()
    

def AajtakVideo():
    print("AajTak Video")
    workbook=xlsxwriter.Workbook('AajTak_Video.xlsx')
    worksheet=workbook.add_worksheet()
    row=0
    column=0
    worksheet.write(row,column,"Heading")
    worksheet.write(row,column+1,"VideoText")
    worksheet.write(row,column+2,"Body")
    worksheet.write(row,column+3,"URL")
    row+=1


    def fetch_html(url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0',
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                print(
                    f"Failed to fetch {url}. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"An error occurred while fetching {url}: {str(e)}")
            return None


    def extract_video_links(html_content):
        video_links = set()  # Use a set to store unique links
        soup = BeautifulSoup(html_content, 'html.parser')
        # Find 'a' tags with 'href' attribute
        video_tags = soup.find_all('a', href=True)

        for tag in video_tags:
            video_url = tag['href']
            if video_url and video_url.startswith('https://www.aajtak'):
                video_links.add(video_url)

        return list(video_links)


    def crawl_website(url, max_links):
        visited_links = set()
        to_visit = [url]
        all_video_links = set()

        while to_visit and len(all_video_links) < max_links:
            current_url = to_visit.pop(0)
            if current_url not in visited_links:
                html_content = fetch_html(current_url)
                if html_content:
                    video_links = extract_video_links(html_content)
                    with open('./aajtak_link.csv', 'a') as f:
                        for link in video_links:
                            if "/video/" in link and link not in all_video_links and len(link) > 60:
                                f.write(link + '\n')
                                all_video_links.add(link)

                    visited_links.add(current_url)
                    to_visit.extend(video_links)


    news_websites = [
        'https://www.aajtak.in/videos'
    ]

    for website in news_websites:
        crawl_website(website, max_links=1)

    print("Crawling completed.")

    csv_file_path = './aajtak_link.csv'

    with open(csv_file_path, 'r') as csv_file:
        video_links = csv.reader(csv_file)
        for r in video_links:
            video_url = r[0]

            try:
                title,video_text,description,url=Aajtak_Video.aajtak(video_url)
                if(title!=""):
                    worksheet.write(row,column,title)
                    worksheet.write(row,column+1,video_text)
                    worksheet.write(row,column+2,description)
                    worksheet.write(row,column+3,url)
                    print(title,video_text,url)
                    row+=1
            except Exception as e:
                print(f"Error processing video URL {video_url}: {str(e)}")

    workbook.close()
    print("AajtakVieos done")
    IndianExpressVideo()
    
    
def IndianExpressVideo():
    print("India Express Vieo")
    workbook=xlsxwriter.Workbook('IndianExpress_Video.xlsx')
    worksheet=workbook.add_worksheet()
    row=0
    column=0
    worksheet.write(row,column,"Heading")
    worksheet.write(row,column+1,"VideoText")
    worksheet.write(row,column+2,"Body")
    worksheet.write(row,column+3,"URL")
    row+=1


    def fetch_html(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            else:
                print(
                    f"Failed to fetch {url}. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"An error occurred while fetching {url}: {str(e)}")
            return None


    def extract_video_links(html_content):
        video_links = set()  # Use a set to store unique links
        soup = BeautifulSoup(html_content, 'html.parser')
        # Find 'a' tags with 'href' attribute
        video_tags = soup.find_all('a', href=True)

        for tag in video_tags:
            video_url = tag['href']
            if video_url.startswith('https://indianexpress'):
                video_links.add(video_url)

        return list(video_links)


    def crawl_website(url, max_links):
        visited_links = set()
        to_visit = [url]
        all_video_links = set()

        while to_visit and len(all_video_links) < max_links:
            current_url = to_visit.pop(0)
            if current_url not in visited_links:
                html_content = fetch_html(current_url)
                if html_content:
                    video_links = extract_video_links(html_content)
                
                    with open('./indianexpress_link.csv', 'a') as f:
                        for link in video_links:
                            if "/videos/" in link and link not in all_video_links and len(link) > 60:
                                f.write(link + '\n')
                                all_video_links.add(link)

                    visited_links.add(current_url)
                    # Add found video links to the queue
                    to_visit.extend(video_links)


    # List of news websites to crawl
    news_websites = [
        'https://indianexpress.com/'
    ]

    for website in news_websites:
        crawl_website(website, max_links=1)

    print("Crawling completed.")


    csv_file_path = './indianexpress_link.csv'

    with open(csv_file_path, 'r') as csv_file:
        video_links = csv.reader(csv_file)
        for r in video_links:
            if len(r) == 0:
                continue
            video_url = r[0]
            try:
                title,video_text,description,url=IndianExpress_Video.indianexpress(video_url)
                if(title!=""):
                    worksheet.write(row,column,title)
                    worksheet.write(row,column+1,video_text)
                    worksheet.write(row,column+2,description)
                    worksheet.write(row,column+3,url)
                    print(title,video_text,url)
                    row+=1
            except Exception as e:
                print(f"Error processing video URL {video_url}: {str(e)}")

    workbook.close()

    print("IndianExpressDone")


    
    
def IndiaToday_Chandigarh():
    print("IndiaToday Chd")
    workbook=xlsxwriter.Workbook('IndiaToday_Chandigarh.xlsx')
    worksheet=workbook.add_worksheet()
    row=0
    column=0
    worksheet.write(row,column,"Heading")
    worksheet.write(row,column+1,"Body")
    worksheet.write(row,column+2,"Category")
    worksheet.write(row,column+3,"URL")
    row+=1
    HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
    r=requests.get('https://www.indiatoday.in/cities/chandigarh-news', headers=HEADERS)
    urls_to_visit=[]
    unique_urls={}
    count=0
    try:
        if(r.status_code==200):
            soup=BeautifulSoup(r.text, 'html.parser')
            for url in soup.findAll('a'):
                try:
                    if(url.has_attr('href')):
                        if("video" not in url['href'].split("/") and "tag" not in url['href'].split("/") and "author" not in url['href'].split("/")):
                            if(url['href'][0]=='/' and "https://www.indiatoday.in/cities/chandigarh"+url['href'] not in unique_urls.keys() and ("chandigarh-news" in url['href'].split("/") or "chandigarh" in url["href"].split("/"))):
                                unique_urls["https://www.indiatoday.in/cities/chandigarh"+url['href']]=True
                                urls_to_visit.append("https://www.indiatoday.in/cities/chandigarh"+url['href'])
                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.indiatoday.in" and url['href'] not in unique_urls.keys() and("chandigarh-news" in url['href'].split("/") or "chandigarh" in url["href"].split("/"))):
                                unique_urls[url['href']]=True
                                urls_to_visit.append(url['href'])
                finally:
                    continue
        while(urls_to_visit and count<20):
                urltoVisit=urls_to_visit[0]
                print(urltoVisit)
                print(count)
                urls_to_visit.pop(0)
            
                if(urltoVisit[0]=='h' and (["tags","tag", "livetv", "video"] not in urltoVisit.split("/"))):
                    try:
                        r=requests.get(urltoVisit, headers=HEADERS)
                        if(r.status_code==200):
                            soup=BeautifulSoup(r.text, 'html.parser')
                            with open('a.txt','w') as f:
                                f.write(r.text)
                            f.close()
                            for url in soup.findAll('a'):
                                try:
                                    if(url.has_attr('href')):
                                        if("video" not in url['href'].split("/") and "tag" not in url['href'].split("/") and "author" not in url['href'].split("/")):
                                            if(url['href'][0]=='/' and "https://www.indiatoday.in/cities/chandigarh"+url['href'] not in unique_urls.keys() and ("chandigarh-news" in url['href'].split("/") or "chandigarh" in url["href"].split("/"))):
                                                unique_urls["https://www.indiatoday.in/cities/chandigarh"+url['href']]=True
                                                urls_to_visit.append("https://www.indiatoday.in/cities/chandigarh"+url['href'])
                                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.indiatoday.in" and url['href'] not in unique_urls.keys() and("chandigarh-news" in url['href'].split("/") or "chandigarh" in url["href"].split("/"))):
                                                unique_urls[url['href']]=True
                                                urls_to_visit.append(url['href'])
                                finally:
                                    continue
                            
                            if(soup.find('div', {'class':'jsx-ace90f4eca22afc7 Story_story__content__body__qCd5E story__content__body widgetgap'}) and (soup.find('html',{'lang':'en'}) or soup.find('html',{'lang':'en-us'})or soup.find('html',{'lang':'en-uk'}))):
                                heading_title=soup.find('div', {'class':'jsx-ace90f4eca22afc7 Story_story__content__body__qCd5E story__content__body widgetgap'}).find('h1')
                                print("Yes")
                                if(soup.find('div', {'class':'jsx-ace90f4eca22afc7 Story_description__fq_4S description'}).findAll('p')):
                                    print("Yes")
                                    
                                    
                                    heading_desc=soup.find('div', {'class':'jsx-ace90f4eca22afc7 Story_description__fq_4S description'}).findAll('p')
                                    news=""
                                    for text in heading_desc:
                                        
                                        news+=text.text
                        
                                    worksheet.write(row,column,heading_title.text)
                                    worksheet.write(row,column+1,news)
                                    if(urltoVisit.split("/")[3]!='cities'):
                                        worksheet.write(row,column+2,urltoVisit.split("/")[3])
                                    else:
                                        worksheet.write(row,column+2,"india")
                                    worksheet.write(row,column+3,urltoVisit)
                                
                                    row+=1
                                    
                                    count+=1
                    finally:
                        continue        
            
        
    finally:
        print("India today Chandigarh finished")
        workbook.close()
        
def JagranChandigarh():
    print("Jagran")
    workbook=xlsxwriter.Workbook('Jagran_Punjab.xlsx')
    worksheet=workbook.add_worksheet()
    row=0
    column=0
    worksheet.write(row,column,"Heading")
    worksheet.write(row,column+1,"Body")
    worksheet.write(row,column+2,"Category")
    worksheet.write(row,column+3,"URL")
    row+=1
    HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
    r=requests.get('https://www.jagran.com/punjab', headers=HEADERS)
    urls_to_visit=[]
    unique_urls={}
    count=0

    try:

        if(r.status_code==200):
            soup=BeautifulSoup(r.text, 'html.parser')
        
            for url in soup.findAll('a'):
                try:
                    if(url.has_attr('href')):
                        if("video" not in url['href'].split("/") and "tag" not in url['href'].split("/") and "author" not in url['href'].split("/")):
                            if(url['href'][0]=='/' and "https://www.jagran.com/punjab"+url['href'] not in unique_urls.keys() and ("chandigarh" in url['href'])):
                                unique_urls["https://www.jagran.com/punjab"+url['href']]=True
                                urls_to_visit.append("https://www.jagran.com/punjab"+url['href'])
                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.jagran.com" and url['href'].split("/")[3]=="punjab" and url['href'] not in unique_urls.keys() and ("chandigarh" in url['href'])):
                                unique_urls[url['href']]=True
                                urls_to_visit.append(url['href'])
                finally:
                    continue


        while(urls_to_visit and count<500):
                urltoVisit=urls_to_visit[0]
                print(count)
                print(urltoVisit)
                urls_to_visit.pop(0)
                if(urltoVisit[0]=='h' and (["tags","tag", "livetv", "videos", "web-stories", "astrology"] not in urltoVisit.split("/"))):
                    try:
                        
                        r=requests.get(urltoVisit, headers=HEADERS)
                        if(r.status_code==200):
                            soup=BeautifulSoup(r.text, 'html.parser')
                            for url in soup.findAll('a'):
                                try:
                                    if(url.has_attr('href')):
                                        if("video" not in url['href'].split("/") and "tag" not in url['href'].split("/") and "author" not in url['href'].split("/")):
                                            if(url['href'][0]=='/' and "https://www.jagran.com/punjab"+url['href'] not in unique_urls.keys() and ("chandigarh" in url['href'])):
                                                unique_urls["https://www.jagran.com/punjab"+url['href']]=True
                                                urls_to_visit.append("https://www.jagran.com/punjab"+url['href'])
                                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.jagran.com" and url['href'].split("/")[3]=="punjab" and url['href'] not in unique_urls.keys() and ("chandigarh" in url['href'])):
                                                unique_urls[url['href']]=True
                                                urls_to_visit.append(url['href'])
                                finally:
                                    continue
                            
                            if(soup.find('h1') and (soup.find('html',{'lang':'hi'}))):
                                heading_title=soup.find('h1').text
                                print("Yes")
                                
                        
                                
                                if(soup.find('div', {'class':'articlecontent'}).findAll('p')):
                                    
                                    
                                    heading_desc=soup.find('div', {'class':'articlecontent'}).findAll('p')
                                    news=""
                                    print("Yes")
                                    for text in heading_desc:
                                        news+=text.text
                                    
                                    news=news.replace("\xa0","")
                                    news=news.replace("\n","")
                                    heading_title=heading_title.replace("\xa0","")
                                    heading_title=heading_title.replace("\n","")
                            
                                    
                                    result=GoogleTranslator(source='auto', target='en').translate(news[0:2200])
                                    headline=GoogleTranslator(source='auto', target='en').translate(heading_title)
                                    print(result)
                                    print(headline)
                                
                                    worksheet.write(row,column,headline)
                                    worksheet.write(row,column+1,result)
                                    worksheet.write(row,column+2,urltoVisit.split("/")[3])
                                    worksheet.write(row,column+3,urltoVisit)
                                
                                    row+=1
                                    
                                    count+=1
                    except Exception as e:
                        print(e)
                    
                    finally:
                        continue        
                    
    except Exception as e:
        print(e)

    finally:
        print("Jagran Finished")
        workbook.close()




    
def index (request):
    print("The Session started")
    thread1 = threading.Thread(target=IndianExpressVideo)
    thread2 = threading.Thread(target=IndiaToday)
    thread3 = threading.Thread(target=IndiaToday_Chandigarh)
    thread4=threading.Thread(target=News18)
    thread7=threading.Thread(target=News18Punj)
    thread8=threading.Thread(target=IndiaTv)
    thread9=threading.Thread(target=JagranChandigarh)
    thread10=threading.Thread(target=AajTak)

    # # Start the threads
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread7.start()
    thread8.start()
    thread9.start()
    thread10.start()
   

    # # Wait for all threads to finish
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread7.join()
    thread8.join()
    thread9.join()
    thread10.join()

    # PreProcessTheData()
    news=[]
    # df=pd.read_excel("Final_Prepped_Data.xlsx")
    # df["VideoText"]=df["VideoText"].fillna("")
    # for ind in df.index:
    #     row={}
    #     row["Title"]=df["Heading"][ind]
    #     row["Description"]=df["HindiBody"][ind]
    #     row["VideoText"]=""
    #     row["URL"]=df["URL"][ind]
    #     row["Categories"]=df["Cat"][ind]
    #     row["Sentiment_Score"]=df["Sentiment"][ind]
    #     news.append(row)
        
    print("PreProcessing Done")
    print("Session Ended")
    

    
    return JsonResponse({"result":"success", "News":news}, safe=False, json_dumps_params={'ensure_ascii': False})
