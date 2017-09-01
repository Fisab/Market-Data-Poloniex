import time
import os
import json
import requests

def to_unix_time(date):
	return int(time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S')))

def to_normal_time(date):
	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(date)))

def get_cur_time():
	return int(time.time())

def check_exist(file_name):
	exist = os.path.isfile(file_name)
	return exist

def format_to_unix(date):
	date = date.split(',')
	if len(date[1]) == 3:
		date[1] = '0' + date[1]
	date = date[0] + ',' + date[1]
	t = int(time.mktime(time.strptime(date, '%d/%m/%Y,%H%M')))
	return t
def format_to_write_data(date):
	#example - 28/09/2017,153 %H:%M:%S
	t = time.strftime('%d/%m/%Y,%H%M', time.localtime(int(date)))
	t = t.replace(',0', ',')
	return t

def req(url):
	try:
		r = requests.get(url, timeout=20)
		d = json.loads(r.text)
		if 'error' in d:
			print('Poloniex timeout. Try after 1 sec.')
			raise Exception
	except Exception:
		while True:
			time.sleep(2)
			r = requests.get(url, timeout=20)
			d = json.loads(r.text)
			if not 'error' in d:
				break
			print('Poloniex timeout. Try after 1 sec.')
	return d

def get_all_data(pair, interval):
	url = 'https://poloniex.com/public?command=returnChartData&currencyPair={pair}&start=0&period={period}'.format(pair=pair, period=interval)
	return req(url)

def get_data_from(pair, interval, s_date):
	url = 'https://poloniex.com/public?command=returnChartData&currencyPair={pair}&start={s_date}&period={period}'.format(pair=pair, period=interval, s_date=s_date)
	return req(url)

def get_ticker():
	url = 'https://poloniex.com/public?command=returnTicker'
	return req(url)

if __name__ == '__main__':
	a = format_to_unix('29/08/2017,125')
	print(a)
	print(to_normal_time(a))