from bs4 import BeautifulSoup
import requests
from time import sleep 
import csv

url = 'https://dou.ua/calendar/page-1/'

headers = {
    'Accept': '*/*',  
    'User-Agent' :'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}


with open('result/result.csv', 'w', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(
        [
            'Event name',
            'Image',
            'Day',
            'Time',
            'Place',
            'Price',
            'Attendees',
            'Tags',
            'Views count'
        ]
     )
    

def get_info(src):
    soup_each_event = BeautifulSoup(src, 'lxml')
    title = soup_each_event.find('div', class_ = 'page-head').find('h1').text

    img = soup_each_event.find('img', class_ = 'event-info-logo').get('src')

    list_event_info_row = soup_each_event.find_all('div', class_ = 'event-info-row')

    list_people_links = []
    res = []
    for row in list_event_info_row:
        each_property =  row.find(class_ = 'dt').text.strip()
        if (len(list_event_info_row) == 4 and list_event_info_row.index(row) == 3)\
        or (len(list_event_info_row) == 5 and list_event_info_row.index(row) == 4):
            people = row.find('div', id = "people").find_all('a')
            for person in people[:-1]:
                list_people_links.append(person.get('href'))
            res.append(list_people_links)

        else:
            value = row.find(class_ = 'dd').text.strip()
            res.append(value)

    if len(res) == 4 or len(res) == 3:
        res.insert(1, '')

    list_tags = soup_each_event.find('div', class_ = 'b-post-tags').find_all('a')
    tags = [t.text for t in list_tags]

    page_views_title = soup_each_event.find('div', class_ = 'b-post-tags').find('span', class_ = 'pageviews').get('title')
    page_views_count = soup_each_event.find('div', class_ = 'b-post-tags').find('span', class_ = 'pageviews').text

    with open(f'result/result.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow (
            (
                title,
                img,     
                res[0],  #day
                res[1],  #time
                res[2],  #place
                res[3],  #price
                ', '.join(res[4]) if len(res) == 5 else '', #attendees
                ', '.join(tags),
                page_views_count
           )
        )
    print('SUCCESS')
    sleep(1)


req_main = requests.get(url, headers=headers)
soup_main = BeautifulSoup(req_main.text, 'lxml')

all_cards = soup_main.find_all(class_ = 'b-postcard') 

for card in all_cards: 
    url_each_event = card.find('h2', class_ = 'title').find('a').get('href')
    req_each_event = requests.get(url_each_event, headers=headers)

    get_info(req_each_event.text)



