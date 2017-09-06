import datetime
import time
import threading
import json
import configparser
import url_parsing as owm
from pymongo import MongoClient
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from gridfs import GridFS

#Make the database Connection
client = MongoClient()
db = client.weather_data
forecast_daily = db.daily_forecast
forecast_hours = db.three_hours_forecast
maps = db.maps
fs = GridFS(db)

config = configparser.ConfigParser()
API_key = '626065bef7e7c8883ff84245fafffa86'
city_list = []
freezing_temp = 2.0
alerts_dict = {}

#Defining Thread subclass for multi-threading
class MyThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print(self.name)

    def config_refresh(self):
        global config, city_list
        config.read("config.ini")
        sections = config.sections()
        cty_lst = config.options(sections[0])
        for city in cty_lst:
            city_list.append([str(city), str(config.get(sections[0], city))])
        time.sleep(10)

    #Three hour forecasts
    def daily_forecast(self):
        global API_key, city_list
        start_time = time.time()
        owm_obj = owm.OWM(API_key)
        for city in city_list:
            forecast_data = owm_obj.daily_forecast(city[1])
            forecast_daily.insert_one(forecast_data)
            for l in forecast_data.get('list'):
                self.daily_alerts(l)

        time.sleep((15) - (time.time() - start_time))
        start_time = time.time()

    def daily_alerts(self, lst):
        global freezing_temp
        temp_dict = lst.get('temp')
        for temp in temp_dict:
            if c_to_f(temp_dict[temp]) < freezing_temp:
                alerts_dict[str(time_converter(lst.get('dt')))] = "Warning! Freezing temperatures -- " + str(datetime.date.fromtimestamp(
        int(lst.get('dt'))))
                break
            rain_lst = lst.get('weather')[0].get('main')
            if "rain" in rain_lst.lower():
                alerts_dict[str(time_converter(lst.get('dt')))] = "Alert! It may rain -- " + str(datetime.datetime.fromtimestamp(
        int(lst.get('dt'))))

        for alert in alerts_dict:
            print(alerts_dict[alert])

    def three_hours_forecast(self):
        global API_key, city_list
        start_time = time.time()
        owm_obj = owm.OWM(API_key)
        for city in city_list:
            forecast_data = owm_obj.three_hours_forecast(city[1])
            forecast_hours.insert_one(forecast_data)
            for l in forecast_data.get('list'):
                self.hourly_alerts(l)

        time.sleep((15) - (time.time() - start_time))
        start_time = time.time()

    def hourly_alerts(self, lst):
        global freezing_temp
        temp = c_to_f(lst.get('main').get('temp'))
        if temp <= freezing_temp:
            alerts_dict[str(time_converter(l.get('dt')))] = "Warning! Freezing temperatures -- " + str(datetime.datetime.fromtimestamp(
        int(lst.get('dt'))))
        rain_lst = lst.get('weather')[0].get('main')
        if "rain" in rain_lst.lower():
            alerts_dict[str(time_converter(lst.get('dt')))] = "Alert! It may rain -- " + str(datetime.datetime.fromtimestamp(
        int(lst.get('dt'))))
        if bool(lst.get('snow')):
            alerts_dict[str(time_converter(l.get('dt')))] = "Alert! It may snow -- " + str(datetime.datetime.fromtimestamp(
        int(lst.get('dt'))))

    def weather_map(self):
        self.layers_list = ['clouds_new', 'precipitation_new', 'pressure_new', 'wind_new', 'temp_new']
        global API_key, city_list
        start_time = time.time()
        owm_obj = owm.OWM(API_key)
        for city in city_list:
            for layers in self.layers_list:
                forecast_url = owm_obj.weather_map(city[0], layers)
                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                map_doc = {st :{str(city[0]):str(forecast_url)}}
                maps.insert_one(map_doc)
        time.sleep((40) - (time.time() - start_time))
        start_time = time.time()

    def display_map(self):
        global maps
        start_time = time.time()

        li = []
        docus = maps.find()
        for ress in docus:
            for key in ress:
                li.append(float(time.mktime(datetime.datetime.strptime(key, "%Y-%m-%d %H:%M:%S").timetuple())))
        li = sorted(li)
        img_url = ress.get(li[-1])
        img = mpimg.imread(img_url)
        plt.imshow(img)
        plt.show(block = False)
        time.sleep((15) - (time.time() - start_time))
        start_time = time.time()
        plt.close()

def time_converter(time):
    converted_time = datetime.date.fromtimestamp(int(time))
    return converted_time

def c_to_f(val):
    f = ((9.0/5)*int(val)) + 32
    return f

thread1 = MyThread('Config_file_thread')
thread2 = MyThread('Daily_forecast_thread')
thread3 = MyThread('Hourly_forecast_thread')
thread4 = MyThread('Weather_maps_thread')
thread5 = MyThread('Weather_map_displayer_thread')

thread1.config_refresh()
thread2.daily_forecast()
thread3.three_hours_forecast()
thread4.weather_map()
thread5.display_map()
