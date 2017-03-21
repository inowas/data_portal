import requests
import unittest
import json

HOST = 'localhost'
PORT = '80'


class WeatherGeneratorTests(unittest.TestCase):
    def test_post(self):

        url = 'http://'+HOST+':'+PORT+'/api-tools/weather-generator-v-1/'
        with open('test_data.json') as json_data:
            data = json.load(json_data)

        response = requests.post(url, json=data)
        self.assertTrue(
            len(data['simulation_dates']) == \
            len(response.json()['simulation_dates']) == \
            len(response.json()['simulated_precip']) == \
            len(response.json()['simulated_t_min']) == \
            len(response.json()['simulated_t_max']) == \
            len(response.json()['simulated_s_rad'])
            )
        print(response.json())
