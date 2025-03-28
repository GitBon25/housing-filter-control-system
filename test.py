import requests

def get_city_guid(city_name):
    url = "https://geo-service.domclick.ru/research/api/v1/autocomplete/regions"
    params = {"name": city_name}
    response = requests.get(url, params=params)
    if response.ok:
        data = response.json()
        if data:
            # Берем первый результат (или фильтруем по нужному типу - "locality")
            city_info = next((item for item in data if item['kind'] == 'locality'), data[0])
            return {
                "name": city_info["name"],
                "guid": city_info["guid"],
                "locality_guid": city_info["locality_guid"],
                "region_guid": city_info["region_guid"],
                "display_name": city_info["display_name"]
            }
    return None

print(get_city_guid("Казань"))
