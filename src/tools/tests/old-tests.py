from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import json



class WeatherGeneratorTests(APITestCase):
    def test_1(self):

        url = reverse('weather_generator')
        with open('tools/test_data.json') as json_data:
            data = json.load(json_data)

        response = self.client.post(url, data, format='json')
        print(response.data)

# from tools import WeatherGenerator
# import pandas as pd
# import matplotlib.pyplot as plt


# df = pd.read_excel("sample_weather.xlsx")
# precip = df['precip'].tolist()
# t_min = df['tmin'].tolist()
# t_max = df['tmax'].tolist()
# s_rad = df['srad'].tolist()
# dates = df['dates'].tolist()
# future_dates = df['future_dates'].tolist()
# print(future_dates)

# weather_generator = WeatherGenerator(
#     precip,
#     srad,
#     tmin,
#     tmax,
#     dates,
#     future_dates
# )

# prec = weather_generator.generate_precipitation()
# simlated_t_min, simlated_t_max, simlated_s_rad = \
# weather_generator.generate_temperatures()




# plt.plot(prec)
# plt.show()
# plt.plot(simlated_t_min)
# plt.show()
# plt.plot(simlated_t_max)
# plt.show()
# plt.plot(simlated_s_rad)
# plt.show()
