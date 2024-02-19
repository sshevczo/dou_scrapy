from bs4 import BeautifulSoup
import requests
from time import sleep 
import csv, sys, os

headers = {
    'Accept': '*/*',  
    'User-Agent' :'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

mode = sys.argv[1] if len(sys.argv) > 1 else os.getenv('PARSING_MODE', 'partial') # default mode - partial

# possible rows names

first_row_name = ['Відбудеться', 'Відбулось', 'Took place', 'Состоялось', 'Date']
second_row_name = ['Початок', 'Time', 'Час', 'Начало', 'Время']
third_row_name = ['Місце', 'Place', 'Место']
fourth_row_name = ['Вартість', 'Price', 'Стоимость']
fifth_row_name = ['Підуть', 'Attendees', 'Пойдут']

all_row_name = [first_row_name, second_row_name, third_row_name, fourth_row_name]

filename = 'result' # default filename

def get_info_each_event(src):
    global filename 

    soup_each_event = BeautifulSoup(src, 'lxml')
    title = soup_each_event.find('div', class_ = 'page-head').find('h1').text

    try:
        img = soup_each_event.find('img', class_ = 'event-info-logo').get('src')
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

    with open(f'result/{filename}.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow (
            (
                title,
                img,     
                res[0],  # d]ay
                res[1],  # time
                res[2],  # place
                res[3],  # price
                ', '.join(res[4]) if len(res) == 5 else '', # attendees
                ', '.join(tags),
                page_views_count
        )
        )

    print('success')
    sleep(0.1)

def pars_full_page(url):
    req_main = requests.get(url, headers=headers)
    soup_main = BeautifulSoup(req_main.text, 'lxml')

    all_cards = soup_main.find_all(class_ = 'b-postcard') 

    for card in all_cards: 
        url_each_event = card.find('h2', class_ = 'title').find('a').get('href')
        req_each_event = requests.get(url_each_event, headers=headers)

        get_info_each_event(req_each_event.text)


def get_count_page():
    
    # automatic calculation of pages in the archive
    url_archive = 'https://dou.ua/calendar/archive/'
    req_archive = requests.get(url_archive, headers=headers)
    soup_archive = BeautifulSoup(req_archive.text, 'lxml')
    count_archive_page = int(soup_archive.find(class_ = 'b-paging').find_all(class_ = 'page')[-1].text)

    for num in range(1, count_archive_page+1):
        pars_full_page(f'https://dou.ua/calendar/archive/{num}/')
    
    # for num in range(50, 0, -1):   # number of pages in archive
    #     pars_full_page(f'https://dou.ua/calendar/archive/{num}/')

    url = 'https://dou.ua/calendar'

    req = requests.get(url, headers=headers)
    soup = BeautifulSoup(req.text, 'lxml')
    count_page = int(soup.find(class_ = 'b-paging').find_all(class_ = 'page')[-1].text)

    for num in range(1, count_page+1):
        pars_full_page(f'https://dou.ua/calendar/page-{num}/')


def start_program(flname='result'):
    global filename
    filename = flname

    with open(f'result/{filename}.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                'Event name',
                'Image',
                'Date',
                'Time',
                'Place',
                'Price',
                'Attendees',
                'Tags',
                'Views count'
            ]
        )

    if mode == 'partial':
        pars_full_page(f'https://dou.ua/calendar/page-1/')

    elif mode == 'full':
        get_count_page()

    else:
        print('unknown mode')



start_program('result_calendar')
