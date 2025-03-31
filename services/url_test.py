from bs4 import BeautifulSoup
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Hash': 'v1:'
}
url = 'https://domclick.ru/card/sale__flat__2064346712'
r = requests.get(url,headers=headers)
with open("res.html", "w", encoding="utf-8") as out:
    print(r.text, file=out)
bs = BeautifulSoup(r.text,"lxml")
description = bs.find('div',class_='J1rDp').text
price = bs.find('div',class_='JfVCK').text
rooms = bs.find('span', {'data-e2e-id': 'Значение'}).text
area_ = bs.find('li',{'data-e2e-id': 'Площадь'})
area = area_.find('span',{'data-e2e-id': 'Значение'}).text
floor_ = bs.find('li',{'data-e2e-id': 'Этаж'})
floor = floor_.find('span',{'data-e2e-id': 'Значение'}).text
location = bs.find('a',class_='w9swr').text
photos_ = bs.find_all('img',class_ = 'picture-image-object-fit--cover-820-3-0-1')
photos = photos_.get_('src')

print(photos)
