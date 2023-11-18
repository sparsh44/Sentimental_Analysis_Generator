import requests
import xlsxwriter
from bs4 import BeautifulSoup

def Tribune():
    
    print("Tribune Chd")
    workbook=xlsxwriter.Workbook('Tribune_Chandigarh.xlsx')
    worksheet=workbook.add_worksheet()
    row=0
    column=0
    worksheet.write(row,column,"Heading")
    worksheet.write(row,column+1,"Body")
    worksheet.write(row,column+2,"Updated_Date")
    worksheet.write(row,column+3,"URL")
    row+=1
    HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
    r=requests.get('https://www.tribuneindia.com/news/city/chandigarh', headers=HEADERS)
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
                            if(url['href'][0]=='/' and "https://www.tribuneindia.com"+url['href'] not in unique_urls.keys() and ("chandigarh-news" in url['href'].split("/") or "chandigarh" in url["href"].split("/"))):
                                
                                unique_urls["https://www.tribuneindia.com"+url['href']]=True
                                urls_to_visit.append("https://www.tribuneindia.com"+url['href'])
                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.tribuneindia.com" and url['href'] not in unique_urls.keys() and("chandigarh-news" in url['href'].split("/") or "chandigarh" in url["href"].split("/"))):
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
                                            if(url['href'][0]=='/' and "https://www.tribuneindia.com"+url['href'] not in unique_urls.keys() and ("chandigarh-news" in url['href'].split("/") or "chandigarh" in url["href"].split("/"))):
                                                
                                                unique_urls["https://www.tribuneindia.com"+url['href']]=True
                                                urls_to_visit.append("https://www.tribuneindia.com"+url['href'])
                                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.tribuneindia.com" and url['href'] not in unique_urls.keys() and("chandigarh-news" in url['href'].split("/") or "chandigarh" in url["href"].split("/"))):
                                                unique_urls[url['href']]=True
                                                urls_to_visit.append(url['href'])
                                finally:
                                    continue
                            
                            if(soup.find('div',{'class':'glb-heading'}) and (soup.find('html',{'lang':'en'}) or soup.find('html',{'lang':'en-us'}) or soup.find('html',{'lang':'en-uk'}))):
                                heading_title=soup.find('div',{'class':'glb-heading'}).find('h1')
                                print("Yes")
                                if(soup.find('div', {'class':'story-desc'}).findAll('p')):
                                    print("Yes")
                                    
                                    
                                    heading_desc=soup.find('div', {'class':'story-desc'}).findAll('p')
                                    news=""
                                    for text in heading_desc:
                                        
                                        news+=text.text
                                        
                                    updated=soup.find('div',{'class':'time-share'}).text
                                    print(updated)
                        
                                    worksheet.write(row,column,heading_title.text)
                                    worksheet.write(row,column+1,news)
                                    worksheet.write(row,column+2,updated)
                                    worksheet.write(row,column+3,urltoVisit)
                                
                                    row+=1
                                    
                                    count+=1
                    finally:
                        continue        
            
        
    finally:
        print("Tribune Chandigarh finished")
        workbook.close()