import requests
import xlsxwriter
from bs4 import BeautifulSoup


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