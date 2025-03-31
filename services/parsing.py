from bs4 import BeautifulSoup
import requests
from server.models.appart_model import ApartUrl
from server.services.db import add_model



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
        ApartUrl(url = urll[i])
        add_model(ApartUrl)

    



