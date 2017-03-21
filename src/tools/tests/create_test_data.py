from datetime import date, datetime, timedelta
import json
import pandas as pd

df = pd.read_excel("sample_weather.xlsx")
precip = df['precip'].tolist()
t_min = df['tmin'].tolist()
t_max = df['tmax'].tolist()
s_rad = df['srad'].tolist()

def make_iso_dates(start, end, delta):
    curr = start
    while curr < end:
        yield curr.isoformat()
        curr += delta

history_dates = [i for i in make_iso_dates(date(2000, 1, 1), date(2010, 12, 31), timedelta(days=1))]
simulation_dates = [i for i in make_iso_dates(date(2100, 1, 1), date(2105, 12, 31), timedelta(days=1))]
print(len(precip), len(history_dates))
data = {
    'history_dates': history_dates,
    'simulation_dates': simulation_dates,
    'precip': precip,
    't_min': t_min,
    't_max': t_max,
    's_rad': s_rad
}
with open('test_data.json', 'w') as outfile:
    json.dump(data, outfile)