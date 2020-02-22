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

def get_shop_comments(trst):
    comments = []
    _request_url = 'https://www.yemeksepeti.com/pasa-doner-arnavutkoy-ilcesi-merkez-mah-istanbul?section=comments'
    response = requests.get(_request_url)
    soup = BeautifulSoup(response.text, "lxml")
    all_comment_elements = soup.findAll("div", {"class": "comments-body"})
    for element in all_comment_elements:
        _comment = {"body": element.findAll("p")[0].text,
                    "speed_point": element.findAll("div", {"class": "speed pointText p10"})[0].text,
                    "serving_point": element.findAll("div", {"class": "serving pointText p10"})[0].text,
                    "flavour_point": element.findAll("div", {"class": "flavour pointText p10"})[0].text
                    }
        comments.append(_comment)
    return comments

if __name__ == '__main__':
    get_shop_comments(YEMEK_SEPETI_CITY_URL)
