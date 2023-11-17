import requests
import xlsxwriter
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from api import Aajtak_Video
from .IndianExpressVideo import IndianExpressVideo
import csv

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


    # def fetch_html(url):
    #     try:
    #         headers = {
    #             'User-Agent': 'Mozilla/5.0',
    #         }
    #         response = requests.get(url, headers=headers)
    #         if response.status_code == 200:
    #             return response.text
    #         else:
    #             print(
    #                 f"Failed to fetch {url}. Status code: {response.status_code}")
    #             return None
    #     except Exception as e:
    #         print(f"An error occurred while fetching {url}: {str(e)}")
    #         return None


    # def extract_video_links(html_content):
    #     video_links = set()  # Use a set to store unique links
    #     soup = BeautifulSoup(html_content, 'html.parser')
    #     # Find 'a' tags with 'href' attribute
    #     video_tags = soup.find_all('a', href=True)

    #     for tag in video_tags:
    #         video_url = tag['href']
    #         if video_url and video_url.startswith('https://www.aajtak'):
    #             video_links.add(video_url)

    #     return list(video_links)


    # def crawl_website(url, max_links):
    #     visited_links = set()
    #     to_visit = [url]
    #     all_video_links = set()

    #     while to_visit and len(all_video_links) < max_links:
    #         current_url = to_visit.pop(0)
    #         if current_url not in visited_links:
    #             html_content = fetch_html(current_url)
    #             if html_content:
    #                 video_links = extract_video_links(html_content)
    #                 with open('./aajtak_link.csv', 'a') as f:
    #                     for link in video_links:
    #                         if "/video/" in link and link not in all_video_links and len(link) > 60:
    #                             f.write(link + '\n')
    #                             all_video_links.add(link)

    #                 visited_links.add(current_url)
    #                 to_visit.extend(video_links)


    # news_websites = [
    #     'https://www.aajtak.in/videos'
    # ]

    # for website in news_websites:
    #     crawl_website(website, max_links=1)

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
    