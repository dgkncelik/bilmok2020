import requests
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
import lxml


class YemekSepetiScraper(object):
    def __init__(self):
        self.yemeksepeti_url = 'https://www.yemeksepeti.com'
        self.city_name = 'istanbul'
        self.es = Elasticsearch(host="127.0.0.1", port=9200)

    def get_city_areas(self, city_url):
        print(city_url)
        areas = []
        response = requests.get(city_url)
        soup = BeautifulSoup(response.text, "lxml")
        all_option_tags = soup.findAll("option")
        for option in all_option_tags:
            area = {"area_name": "", "area_url": "", "city_name": self.city_name}
            option_url = option.get("data-url")
            if option_url and ("ilce" in option_url or "mah" in option_url):
                area['area_name'] = option.text
                area['area_url'] = '%s%s' % (self.yemeksepeti_url, option_url)
                areas.append(area)
        return areas

    def get_area_shops(self, area):
        print(area)
        shops = []
        request_url = '%s%s' % (area['area_url'], '#ors:false')
        response = requests.get(request_url)
        soup = BeautifulSoup(response.text, "lxml")
        all_restaurant_elements = soup.findAll("a", {"class": "restaurantName"})
        for element in all_restaurant_elements:
            shop = {"shop_name": element.find("span").text,
                    "shop_link": '%s%s' % (self.yemeksepeti_url, element.get("href"))}
            shops.append(shop)
        return shops

    def get_shop_comments(self, shop):
        print(shop)
        comments = []
        request_url = '%s?section=comments' % shop['shop_link']
        response = requests.get(request_url)
        soup = BeautifulSoup(response.text, "lxml")
        all_comment_elements = soup.findAll("div", {"class": "comments-body"})
        for element in all_comment_elements:
            try:
                comment = {"body": element.findAll("p")[0].text,
                           "speed_point": int(element.findAll("div", {"class": "speed"})[0].text.replace('Hız: ', '')),
                           "flavour_point": int(
                               element.findAll("div", {"class": "flavour"})[0].text.replace('Lezzet: ', '')),
                           "serving_point": int(
                               element.findAll("div", {"class": "serving"})[0].text.replace('Servis: ', ''))}
            except Exception:
                continue
            comments.append(comment)
        return comments

    def analyze_by_elasticsearch(self, document):
        _body = '%s %s' % (document['body'], document['shop_name'])
        query = {
            "query": {
                "percolate": {
                    "field": "query",
                    "document": {
                        "body": _body
                    }
                }
            }
        }
        result = self.es.search(index='analyze-index', body=query)
        matches = result['hits']['hits']
        if matches:
            for m in matches:
                document['food_categories'].append(m['_source']['category'])
        return document

    def index_to_elasticsearch(self, document):
        return self.es.index(index='document-index', body=document)

    def run(self):
        city_url = '%s/%s' % (self.yemeksepeti_url, self.city_name)
        areas = self.get_city_areas(city_url)
        for area in areas:
            shops = self.get_area_shops(area)
            for shop in shops:
                raw_comments = self.get_shop_comments(shop)
                for raw in raw_comments:
                    document = {}
                    document["city"] = self.city_name
                    document["shop_name"] = shop["shop_name"]
                    document["area_name"] = area["area_name"]
                    document["body"] = raw["body"]
                    document["serving_point"] = raw["serving_point"]
                    document["speed_point"] = raw["speed_point"]
                    document["flavour_point"] = raw["flavour_point"]
                    document["food_categories"] = []
                    document = self.analyze_by_elasticsearch(document)
                    self.index_to_elasticsearch(document)


if __name__ == '__main__':
    YemekSepetiScraper().run()
