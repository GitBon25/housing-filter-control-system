from bs4 import BeautifulSoup
import requests
from server.models.appart_model import Apart
from server.services.db import add_model

def parsing(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Hash': 'v1:'
    }
    r = requests.get(url,headers=headers)
    bs = BeautifulSoup(r.text,"lxml")
    description = bs.find('div',class_='J1rDp').text
    price = bs.find('div',class_='JfVCK').text
    rooms = bs.find('span', {'data-e2e-id': 'Значение'}).text
    area_ = bs.find('li',{'data-e2e-id': 'Площадь'})
    area = area_.find('span',{'data-e2e-id': 'Значение'}).text
    floor_ = bs.find('li',{'data-e2e-id': 'Этаж'})
    floor = floor_.find('span',{'data-e2e-id': 'Значение'}).text
    location = bs.find('a',class_='w9swr').text
    return Apart(
        url = url,
        description = description,
        price = price,
        rooms = rooms,
        area = area,
        floor = floor,
        location = location
    )


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Hash': 'v1:'
}
for i in range(10):
    url = f'https://domclick.ru/search?deal_type=sale&category=living&offer_type=flat&offer_type=layout&offset={i*20}'
    r = requests.get(url,headers=headers)
    bs = BeautifulSoup(r.text,"lxml")
    link = bs.find_all('a', class_='a4tiB2')
    urll = [link.get('href') for link in link if link.get('href')]
    for i in range(20):
        add_model(model = parsing(urll[i]))

    



