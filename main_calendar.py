from bs4 import BeautifulSoup
import requests
import dateparser
from time import sleep 
import csv, sys, os
from sqlalchemy.orm import sessionmaker
from event_models import Event, engine
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
Session = sessionmaker(bind=engine)
session = Session()

headers = {
    'Accept': '*/*',  
    'User-Agent' :'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

# possible rows names

first_row_name = ['Відбудеться', 'Відбулось', 'Took place', 'Состоялось', 'Date']
second_row_name = ['Початок', 'Time', 'Час', 'Начало', 'Время']
third_row_name = ['Місце', 'Place', 'Место']
fourth_row_name = ['Вартість', 'Price', 'Стоимость']
fifth_row_name = ['Підуть', 'Attendees', 'Пойдут']

all_row_name = [first_row_name, second_row_name, third_row_name, fourth_row_name]

filename = 'result' # default filename

def get_info_each_event(src, sleep_pause):
    global filename 

    soup_each_event = BeautifulSoup(src, 'lxml')
    title = soup_each_event.find('div', class_ = 'page-head').find('h1').text

    try:
        img = soup_each_event.find('img', class_ = 'event-info-logo').get('src').split('/')[-2:]
        url_img = '/'.join(img)
        
    except Exception:
        img = ''

    list_event_info_row = soup_each_event.find_all('div', class_ = 'event-info-row')

    list_people_links = []
    res = []
    value_dict = {}
    for row in list_event_info_row:
        value_dict[row.find(class_ = 'dt').text.strip()] = row.find(class_ = 'dd').text.strip()
    
    for row_name in all_row_name:
        value_for_res = ''
        for name in row_name:
            if name in value_dict:
                value_for_res = value_dict[name]

        res.append(value_for_res)

    last_item = value_dict.popitem()
    if '\n' in last_item[0]:
        main_name_row = last_item[0].split('\n')[0].strip()
        if main_name_row in fifth_row_name:
            people = row.find('div', id = "people").find_all('a')

            for person in people[:-1]:
                list_people_links.append(person.get('href'))
            res.append(list_people_links)

    elif last_item[0] in fifth_row_name:
        people = row.find('div', id = "people").find_all('a')

        for person in people[:-1]:
            list_people_links.append(person.get('href'))
        res.append(list_people_links)
    else:
        res.append('')

    try:
        list_tags = soup_each_event.find('div', class_ = 'b-post-tags').find_all('a')
        tags = [t.text for t in list_tags]
    except Exception:
        tags = ''

    page_views_count = soup_each_event.find('div', class_ = 'b-post-tags').find('span', class_ = 'pageviews').text
    
    date_time = res[0] + ' ' + res[1] if res[0] and res[1] else ''
    if date_time:
        date_time_obj = dateparser.parse(date_time)
        if date_time_obj is not None:
            unix_timestamp = int(date_time_obj.timestamp())
        else:
            unix_timestamp = 0  # Или любое другое значение по умолчанию, если дата и время не распознаны
    else:
        unix_timestamp = 0  # Или любое другое значение по умолчанию, если строка даты и времени пустая # Или любое другое значение по умолчанию, если дата и время не распознаны
    
    date_time = datetime.fromtimestamp(unix_timestamp)
    # formatted_date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
    
    print(date_time)

    with open(f'result/{filename}.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow (
            (
                title,
                url_img,
                date_time, # time
                res[2],  # place
                res[3],  # price
                ', '.join(res[4]) if len(res) == 5 else '', # attendees
                ', '.join(tags),
                page_views_count
        )
        )

    event = Event(
        title=title,
        img=url_img,
        date_time=date_time,
        place=res[2],
        price=res[3],
        attendees=len(res[4]) if len(res) == 5 else ''
    )

    session.add(event)
    session.commit()

    print('success')
    sleep(sleep_pause)

def pars_full_page(url, sleep_pause):
    req_main = requests.get(url, headers=headers, proxies=proxies)
    soup_main = BeautifulSoup(req_main.text, 'lxml')

    all_cards = soup_main.find_all(class_ = 'b-postcard') 

    for card in all_cards: 
        url_each_event = card.find('h2', class_ = 'title').find('a').get('href')
        req_each_event = requests.get(url_each_event, headers=headers, proxies=proxies)

        get_info_each_event(req_each_event.text, sleep_pause)


def get_count_page(sleep_pause):
    
    # automatic calculation of pages in the archive
    url_archive = 'https://dou.ua/calendar/archive/'
    req_archive = requests.get(url_archive, headers=headers, proxies=proxies)
    soup_archive = BeautifulSoup(req_archive.text, 'lxml')
    count_archive_page = int(soup_archive.find(class_ = 'b-paging').find_all(class_ = 'page')[-1].text)

    for num in range(1, count_archive_page+1):
        pars_full_page(f'https://dou.ua/calendar/archive/{num}/', sleep_pause)
    
    # for num in range(50, 0, -1):   # number of pages in archive
    #     pars_full_page(f'https://dou.ua/calendar/archive/{num}/', sleep_pause)

    url = 'https://dou.ua/calendar'

    req = requests.get(url, headers=headers, proxies=proxies)
    soup = BeautifulSoup(req.text, 'lxml')
    count_page = int(soup.find(class_ = 'b-paging').find_all(class_ = 'page')[-1].text)

    for num in range(1, count_page+1):
        pars_full_page(f'https://dou.ua/calendar/page-{num}/', sleep_pause)


def start_program(flname, sleep_pause):
    global filename
    filename = flname

    with open(f'result/{filename}.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                'Event name',
                'Image',
                'DateTime',
                
                'Place',
                'Price',
                'Attendees',
                'Tags',
                'Views count'
            ]
        )
    if isinstance(sleep_pause, str):
        try:
            sleep_pause = int(sleep_pause)
        except Exception:
            sleep_pause = 0.1 

    if mode == 'True':
        pars_full_page(f'https://dou.ua/calendar/page-1/', sleep_pause)

    elif mode == 'False':
        get_count_page(sleep_pause)
    else:
        print('unknown mode')

    events = session.query(Event).all()
    for event in events:
        print(event.title, event.date_time)

if __name__ == '__main__':
    flname = os.getenv('FILENAME', 'result')
    sleep_pause = float(os.getenv('SLEEP_PAUSE', 0.1))
    proxy = os.getenv("PROXY", None)

    proxies = {"http": proxy, "https": proxy} if proxy else None
    mode = os.getenv('TEST_MODE', False) # default mode - full

    start_program(flname=flname, sleep_pause=sleep_pause)