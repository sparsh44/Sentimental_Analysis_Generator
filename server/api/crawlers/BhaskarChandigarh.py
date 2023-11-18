import requests
import xlsxwriter
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

def Bhaskar():

    print("Bhaskar Chd")
    workbook=xlsxwriter.Workbook('Bhaskar_Chandigarh.xlsx')
    worksheet=workbook.add_worksheet()
    row=0
    column=0
    worksheet.write(row,column,"Heading")
    worksheet.write(row,column+1,"Body")
    worksheet.write(row,column+2,"Updated_Date")
    worksheet.write(row,column+3,"URL")
    row+=1
    HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
    r=requests.get('https://www.bhaskar.com/local/chandigarh', headers=HEADERS)
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
                            if(url['href'][0]=='/' and "https://www.bhaskar.com"+url['href'] not in unique_urls.keys() and ("chandigarh-news" in url['href'].split("/") or "chandigarh" in url["href"].split("/"))):
                                
                                unique_urls["https://www.bhaskar.com"+url['href']]=True
                                urls_to_visit.append("https://www.bhaskar.com"+url['href'])
                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.bhaskar.com" and url['href'] not in unique_urls.keys() and("chandigarh-news" in url['href'].split("/") or "chandigarh" in url["href"].split("/"))):
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
                            for url in soup.findAll('a'):
                                try:
                                    if(url.has_attr('href')):
                                        if("video" not in url['href'].split("/") and "tag" not in url['href'].split("/") and "author" not in url['href'].split("/")):
                                            if(url['href'][0]=='/' and "https://www.bhaskar.com"+url['href'] not in unique_urls.keys() and ("chandigarh-news" in url['href'].split("/") or "chandigarh" in url["href"].split("/"))):
                                
                                                unique_urls["https://www.bhaskar.com"+url['href']]=True
                                                urls_to_visit.append("https://www.bhaskar.com"+url['href'])
                                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.bhaskar.com" and url['href'] not in unique_urls.keys() and("chandigarh-news" in url['href'].split("/") or "chandigarh" in url["href"].split("/"))):
                                                unique_urls[url['href']]=True
                                                urls_to_visit.append(url['href'])
                                finally:
                                    continue
                            
                            if(soup.find('div',{'class':'a88a1c42'}) and (soup.find('html',{'lang':'hi'}))):
                                heading_title=soup.find('div',{'class':'a88a1c42'}).find('h1').text
                                print("Yes")
                                if(soup.find('p', {'class':'c4fb714d'})):
                                    print("Yes")
                                    
                                    
                                    heading_desc=soup.find('p', {'class':'c4fb714d'}).text
                                        
                                    updated=soup.find('span',{'class':'c49a6b85'}).text
                                    print(updated)
                                    result=GoogleTranslator(source='auto', target='en').translate(heading_desc)
                                    headline=GoogleTranslator(source='auto', target='en').translate(heading_title)
                                    updatedEng=GoogleTranslator(source='auto', target='en').translate(updated)
                            
                                    print(result)
                                    print(headline)
                        
                        
                                    worksheet.write(row,column,headline)
                                    worksheet.write(row,column+1,result)
                                    worksheet.write(row,column+2,updatedEng)
                                    worksheet.write(row,column+3,urltoVisit)
                                
                                    row+=1
                                    
                                    count+=1
                    finally:
                        continue        
            
        
    finally:
        print("Bhaskar Chandigarh finished")
        workbook.close()