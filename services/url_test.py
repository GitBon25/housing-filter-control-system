from bs4 import BeautifulSoup
import requests

payload = {
    'sale_price__lte': 10000000,
    'area__gte': 4,
    'rooms': 3
}

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
description = bs.find('div',class_='J1rDp').text
description = bs.find('div',class_='J1rDp').text
description = bs.find('div',class_='J1rDp').text
print(description,price,rooms)