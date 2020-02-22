import requests
from bs4 import BeautifulSoup
import lxml


YEMEK_SEPETI_CITY_URL = 'https://www.yemeksepeti.com/istanbul'


def get_areas(city_url):
    urls = []
    response = requests.get(city_url)
    soup = BeautifulSoup(response.text, "lxml")
    all_option_tags = soup.findAll("option")
    for option in all_option_tags:
        _option = option.get("data-url")
        if _option and ('ilce' in _option or 'mah' in _option):
            urls.append(option.get("data-url"))
    return urls

def get_area_shops(area_url_suffix):
    shops = []
    _reqeust_url = 'https://www.yemeksepeti.com/istanbul/arnavutkoy-ilcesi-anadolu-mah'
    response = requests.get(_reqeust_url)
    soup = BeautifulSoup(response.text, "lxml")
    all_restaurant_elements = soup.findAll("a", {"class": "restaurantName"})
    for element in all_restaurant_elements:
        shops.append({"restaurantName": element.find("span").text, "restaurantLink": element.get("href")})
    return shops

if __name__ == '__main__':
    get_area_shops(YEMEK_SEPETI_CITY_URL)
