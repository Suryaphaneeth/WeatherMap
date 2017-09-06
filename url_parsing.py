import urllib.request
import json
import time
import datetime
from dateutil import parser

class OWM(object):
    def __init__(self, API_key):
        self.API_key = API_key
        self.latitude = 0
        self.longitude = 0

    def three_hours_forecast(self, city_code):
        self.api_url = "http://api.openweathermap.org/data/2.5/forecast?id={}&mode=json&units=metric&APPID={}".format(city_code, self.API_key)
        self.data_dictionary = self.get_dict(self.api_url)
        return self.data_dictionary

    def daily_forecast(self, city_code):
        self.api_url = "http://api.openweathermap.org/data/2.5/forecast/daily?id={}&cnt=16&mode=json&units=metric&APPID={}".format(city_code, self.API_key)
        self.data_dictionary = self.get_dict(self.api_url)
        return self.data_dictionary

    def weather_map(self, city):
        url_list = {}
        self.lat = self.getLatitude(city)
        self.lon = self.getLongitude(city)
        self.layers_list = ['clouds_new', 'precipitation_new', 'pressure_new', 'wind_new', 'temp_new']
        for layer in self.layers_list:
            api_url = "http://tile.openweathermap.org/{}/5/{}/{}.png?appid={}".format(self.lat, self.lon, self.API_key, layer)
            datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
            url_list = {strtime:{str(layer):str(api_url)}}
        return url_list

    def get_dict(self, api_url):
        with urllib.request.urlopen(api_url) as url:
            self.output_data = url.read().decode('utf-8')
        self.data_dict = json.loads(self.output_data)
        url.close()
        return self.data_dict

    def setLatitude(self, city):
        self.latitude = input("Enter latitude information of {}:".format(city))

    def getLatitude(self, city):
        if self.latitude == 0:
            self.setLatitude(city)
        return self.latitude

    def setLongitude(self, city):
        self.longitude = input("Enter longitude information of {}:".format(city))

    def getLongitude(self, city):
        if self.longitude == 0:
            self.setLongitude(city)
        return self.longitude
