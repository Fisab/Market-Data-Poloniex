import requests
import json

url = 'https://poloniex.com/public?command=returnTicker'

need_intervals = [300, 900, 1800, 7200, 86400]

r = requests.get(url)

data = json.loads(r.text)

res = ''

for i in data.keys():
	for j in need_intervals:
		res += '\n' + i + ',' + str(j) + ',' + 'open_high_low_close_volume,./data/'

f = open('config.csv', 'r')
text = f.read()
f = open('config.csv', 'w')
f.write(text+res)