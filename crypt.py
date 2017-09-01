import requests
import json
import time
import os.path
import sys

import tools

import ticker
import threading

tickIntervals = {
	'300': '5min',
	'900': '15min', 
	'1800': '30min',
	'7200': '2h',
	'14400': '4h',
	'86400': '1d'
}

def gen_name(pair, interval, types):
	name = ''
	t = types.split('_')
	for i in t:
		name += i[0].upper()

	name += '_' + pair.upper()
	name += '_' + tickIntervals[str(interval)] + '.csv'

	return name

def read_conf():
	f = open('config.csv', 'r')
	i = 0
	result = []
	for line in f:
		if i != 0:
			data = line.replace('\n', '').split(',')
			it_ticker = False
			if len(data) == 5:
				it_ticker = True
			data = {
				'pair': data[0],
				'interval': data[1],
				'headings': data[2],
				'file_path': data[3]
			}
			
			if not data['interval'] in tickIntervals:
				continue
			result.append(data)
		i += 1
	return result

def get_last_date(file_name):
	f = open(file_name, 'r')
	lines = f.readlines()
	#print(len(lines))
	last_line = lines[-1]
	ind = [i for i, x in enumerate(last_line) if x == ',']
	last_line = last_line[0:ind[1]]
	return last_line

def create_file(rows, file_name):
	rows = rows.split('_')
	result = 'Date,Time'
	for i in rows:
		result += ',' + i.title()
	
	f = open(file_name, 'w')
	f.write(result)
	f.close()


def write_to_file(file_name, text, exist):
	if exist:
		file = open(file_name, 'r')
		old_data = file.read()
	else:
		old_data = ''
	file = open(file_name, 'w')
	file.write(old_data + text)
	file.close()

def format_data(data, format):
	res = ''

	need_rows = format.split('_')
	for i in data:
		res += '\n' + tools.format_to_write_data(i['date'])
		for j in need_rows:
			if j == 'volume':
				i[j] = int(i[j] * 1000000)
				res += ',%s' % str(i[j])
			else:
				res += ',' + str('{0:f}'.format(i[j]))

	return res

def get_last_line(file_name):
	file = open(file_name, 'r')
	data = file.readlines()
	if len(data) > 0:
		#print(repr(data[-1]))
		#print(data[-1] == ' ', 'asdf')
		return data[-1]

def check_is_ticker(data):
	data = data.split(',')
	if data[-1] == '0':
		return True
	else:
		return False

def delete_last_line(file_name):
	file = open(file_name, 'r')
	data = file.readlines()
	file = open(file_name, 'w')
	del data[-1]
	data[len(data)-1] = data[len(data)-1][:-1]
	file.writelines(data)

def main():
	config = read_conf()
	for data in config:
		name = gen_name(data['pair'], data['interval'], data['headings'])
		exist = tools.check_exist(data['file_path'] + name)
		print(name)
		a = int(time.time())
		if not exist:
			create_file(data['headings'], data['file_path'] + name)
			res = tools.get_all_data(data['pair'], data['interval'])
			res = format_data(res, data['headings'])
			write_to_file(data['file_path'] + name, res, True)
		else:
			last_date = get_last_date(data['file_path'] + name)
			if last_date == 'Date,Time':#empty file
				res = tools.get_all_data(data['pair'], data['interval'])
				res = format_data(res, data['headings'])
				write_to_file(data['file_path'] + name, res, True)
			else:
				last_date = tools.format_to_unix(last_date)
				res = tools.get_data_from(data['pair'], data['interval'], last_date)
				if len(res) == 1 and res[0]['date'] == 0:
					continue
				if res == []:
					continue
				#check old data ticker
				old_data = get_last_line(data['file_path'] + name)
				is_ticker = check_is_ticker(old_data)
				if not is_ticker:
					res.pop(0)
				res = format_data(res, data['headings'])
				if res != '':
					if is_ticker:
						delete_last_line(data['file_path'] + name)
					write_to_file(data['file_path'] + name, res, True)
					continue
				#print(repr(res))
				#write_to_file(data['file_path'] + name, res, True)

				#check if need ticker
				file_name = 'ticker_' + data['pair'] + '_' + data['interval'] + '.json'
				last_date = get_last_date(data['file_path'] + name)
				last_date = tools.format_to_unix(last_date)
				ticker_exist = tools.check_exist('./tickers/' + file_name)
				if ticker_exist:
					new_charts = ticker.get_file_data(file_name)
					new_chart = ''
					if tools.get_cur_time() % int(data['interval']) > 10:
						continue
					for new_chart_ in new_charts:
						if last_date + int(data['interval']) == new_chart_['timestamp'] and tools.get_cur_time() > new_chart_['timestamp']:
							new_chart = new_chart_
							break
					if new_chart == '':
						continue
					#print(322, last_date + int(data['interval']), new_chart['timestamp'])
					#print(last_date + int(data['interval']), new_chart['timestamp'])
					#print(last_date + int(data['interval']) == new_chart['timestamp'], tools.get_cur_time() > new_chart['timestamp'])
					if last_date + int(data['interval']) == new_chart['timestamp'] and tools.get_cur_time() > new_chart['timestamp']:
						print('set ticker')
						#format data
						res += '\n' + tools.format_to_write_data(new_chart['timestamp'])
						for g in data['headings'].split('_'):
							if g != 'volume':
								res += ',' + new_chart[g]
							else:
								res += ',0'
				#print(new_chart['timestamp'], last_date)
				#print(tools.to_normal_time(new_chart['timestamp']), tools.to_normal_time(last_date))
				if is_ticker:
					delete_last_line(data['file_path'] + name)
				if res != '':
					write_to_file(data['file_path'] + name, res, True)
		#print(int(time.time())-a)
		time.sleep(2)


if __name__ == '__main__':
	ticker_thread = threading.Event()
	t1 = threading.Thread(target=ticker.main)
	t1.start()
	while True:
		#print('update', int(time.time()))
		main()
		print('sleep', tools.to_normal_time(int(time.time())))
		time.sleep(10)
