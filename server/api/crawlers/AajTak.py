import requests
import xlsxwriter
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

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
    