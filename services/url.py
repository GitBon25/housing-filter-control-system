import requests
import logging



def find_flats(rooms, price, area, location, deal):
    url1 = "https://geo-service.domclick.ru/research/api/v1/autocomplete/regions"
    params = {"name": location}
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url1, params=params, headers=headers)
    data = response.json()

    items = data.get("answer", {}).get("items", [])

    for item in items:
        if item.get("name").lower() == location.lower():
            guid = item.get("guid")
            break
    
    url2 = "https://bff-search-web.domclick.ru/api/offers/v1"
    if deal == 'rent':
        price_key = "rent_price__lte"
    else:
        price_key = "sale_price__lte"

    params = {
        "address": guid,
        "offset": 0,
        "limit": 5,
        "sort": "qi",
        "sort_dir": "desc",
        "deal_type": deal,
        "category": "living",
        "offer_type": ["flat", "layout"],
        price_key: price,
        "rooms": rooms,
        "area_lte": area
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Origin": "https://domclick.ru",
        "Referer": "https://domclick.ru/",
    }

    logging.info(f"🔍 Параметры запроса: {params}")

    response = requests.get(url2, headers=headers, params=params)

    logging.info(f"🌐 URL запроса: {response.url}")

    if response.status_code != 200:
        return [{"caption": f"Ошибка запроса: {response.status_code}", "photo_url": ""}]

    data = response.json()
    items = data.get("result", {}).get("items", [])

    if not items:
        return [{"caption": "🔍 Квартиры не найдены по заданным параметрам.", "photo_url": ""}]

    results = []

    for i, item in enumerate(items, start=1):
        address = item.get("address", {}).get("displayName", "Адрес не указан")
        flat_price = item.get("price", "Цена не указана")
        flat_area = item.get("objectInfo", {}).get("area", "—")
        flat_rooms = item.get("objectInfo", {}).get("rooms", "—")
        floor = item.get("objectInfo", {}).get("floor", "—")
        floors_total = item.get("house", {}).get("floors", "—")

        full_description = item.get(
            "description", "").replace('\n', ' ').strip()
        description = (
            full_description[:297] + "…") if len(full_description) > 300 else full_description

        path = item.get("path", "")
        photo_url = item.get("photos", [{}])[0].get("url", "")
        photo_full = f"https://img.dmclk.ru{photo_url}" if photo_url else ""

        caption = (
            f"🏠 Квартира #{i}, {"аренда" if deal == "rent" else "покупка"}\n"
            f"📍 {address}\n"
            f"💰 {flat_price:,} ₽\n"
            f"📐 {flat_area} м², Комнат: {flat_rooms if flat_rooms != 0 else "Студия"}\n"
            f"🏢 Этаж: {floor} из {floors_total}\n"
            f"📝 {description}\n"
            f"🔗 {path}"
        )

        results.append({
            "photo_url": photo_full,
            "caption": caption
        })

    return results