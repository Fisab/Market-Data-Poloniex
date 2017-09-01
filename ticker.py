import tools
import time
import json
from os import listdir, remove

need_intervals = [300, 900, 1800, 7200, 86400]

path = './tickers/'

tickIntervals = {
	'300': '5min',
	'900': '15min', 
	'1800': '30min',
	'7200': '2h',
	'14400': '4h',
	'86400': '1d'
}

def write_to_file(file_name, data):
	with open(path + file_name, 'w') as outfile:
		json.dump(data, outfile, indent=4)

def get_file_data(file_name):
	with open(path + file_name) as data_file:
		data = json.load(data_file)
	return data

def check_timestamp(timestamp, interval):
	cur_time = int(time.time())
	if timestamp < cur_time:
		return timestamp + interval
	else:
		return False

def get_last_candle(data):
	max_timestamp = 0
	for i in data:
		if i['timestamp'] > max_timestamp:
			max_timestamp = i['timestamp']
	for i in data:
		if i['timestamp'] == max_timestamp:
			return i

def main():
	update = False
	old_files = listdir(path)
	for file in old_files:
		remove(path + file)
	###
	while True:
		cur_time = tools.get_cur_time()
		ticker = tools.get_ticker()
		for i in tickIntervals.keys():
			for j in ticker.keys():
				file_name = 'ticker_' + j + '_' + str(i) + '.json'
				exist = tools.check_exist(path + file_name)

				if exist:
					all_data = get_file_data(file_name)
					data = get_last_candle(all_data)

					new_timestamp = check_timestamp(data['timestamp'], int(i))

					if new_timestamp == False:
						rewrite = False
						if float(data['high']) < float(ticker[j]['last']):
							data['high'] = '{0:f}'.format(float(ticker[j]['last']))
							rewrite = True
						if float(data['low']) > float(ticker[j]['last']):
							data['low'] = '{0:f}'.format(float(ticker[j]['last']))
							rewrite = True
						if rewrite:
							for o in range(len(all_data)):
								if all_data[o]['timestamp'] == data['timestamp']:
									all_data[o] = data
									break

							write_to_file(file_name, all_data)
					elif data['timestamp'] != 0:
						l = '{0:f}'.format(float(ticker[j]['last']))
						result = []
						res = {'timestamp': data['timestamp'], 'open': data['open'], 'high': data['high'], 'low': data['low'], 'close': l}
						result.append(res)
						res = {'timestamp': new_timestamp, 'open': l, 'high': l, 'low': l, 'close': l}
						result.append(res)
						write_to_file(file_name, result)

				if not exist and cur_time % int(i) < 20:#need create new file
					cur_time -= cur_time % int(i)
					l = '{0:f}'.format(float(ticker[j]['last']))
					result = [{'timestamp': cur_time + int(i), 'open': l, 'high': l, 'low': l, 'close': l}]
					write_to_file(file_name, result)
		time.sleep(2)



if __name__ == '__main__':
	while True:
		main()
		time.sleep(2)