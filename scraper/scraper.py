import requests
from bs4 import BeautifulSoup
import lxml


class YemekSepetiScraper(object):
    def __init__(self):
        self.yemeksepeti_url = 'https://www.yemeksepeti.com/'
        self.city_name = 'istanbul'

    def get_city_areas(self, city_url):
        areas = []
        response = requests.get(city_url)
        soup = BeautifulSoup(response.text, "lxml")
        all_option_tags = soup.findAll("option")
        for option in all_option_tags:
            area = {"name": "", "area_url": ""}
            option_url = option.get("data-url")
            if option_url and ("ilce" in option_url or "mah" in option_url):
                area['area_url'] = option_url
                areas.append(area)
        return areas

    def get_area_shops(self, area):
        shops = []
        request_url = area['area_url']
        response = requests.get(request_url)
        soup = BeautifulSoup(response.text, "lxml")
        all_restaurant_elements = soup.findAll("a", {"class": "restaurantName"})
        for element in all_restaurant_elements:
            shop = {"restaurant_name": element.find("span").text,
                    "restaurant_link":  element.get("href")}
            shops.append(shop)
        return shops

    def get_shop_comments(self, shop):
        comments = []
        request_url = '%s?section=comments' % shop['restaurant_link']
        response = requests.get(request_url)
        soup = BeautifulSoup(response.text, "lxml")
        all_comment_elements = soup.findAll("div", {"class": "comments-body"})
        for element in all_comment_elements:
            comment = {"body": element.findAll("p")[0].text,
                       "speed_point": element.findAll("div", {"class": "speed pointText p10"})[0].text,
                       "flavour_point": element.findAll("div", {"class": "flavour pointText p10"})[0].text}
            comments.append(comment)
        return comments

    def analyze_by_elasticsearch(self, comments):
        return None

    def index_to_elasticsearch(self, comments):
        return None

    def run(self):
        city_url = '%s/%s' % (self.yemeksepeti_url, self.city_name)
        areas = self.get_city_areas(city_url)
        for area in areas:
            shops = self.get_area_shops(area)
            for shop in shops:
                comments = self.get_shop_comments(shop)
                comments = self.analyze_by_elasticsearch(comments)
                self.index_to_elasticsearch(comments)


if __name__ == '__main__':
    YemekSepetiScraper().run()
