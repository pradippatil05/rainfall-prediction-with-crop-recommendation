import requests
import random
import pandas as pd

cropdf = pd.read_csv("Crop_recommendation.csv")

adi_ApIKeY = 'ae77e8c1a138c780cd332d478fa000ea'

class CROPAPI:
    def data(self, latitude, longitude):

        openWeatherResponse = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid=4c61f798e1507fb0f06b70da4c7d41c8')

        data = openWeatherResponse.json()['main']
        temprature = data['temp']
        humidity = data['humidity']
        p = random.choice(cropdf['P'])
        k = random.choice(cropdf['K'])
        ph = random.choice(cropdf['ph'])
        rainfall = random.choice(cropdf['rainfall'])
        # print(temprature)
        # print(humidity)
        return temprature, humidity
        

