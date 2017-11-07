import time
import datetime as dt
import os
import csv
import sys
import copy
import numpy as np
import os.path
import datetime as dt

def launch_proceedure(earliestDate, watchlist, path, log_file):
	#checks that everything is ready to go on program launch

	#check that all the files for all the codes exist
	#makes sure that data is up to date
	#if it's not up to date, removes that code for the week
	# returns the codes to check
	# if there is no folder path + "data/" then we've got big problems and program can't run
	# if there is not data in data/stock_data/ then run full initialisation
	
	todays_date = dt.date.today().strftime("%Y%m%d")

	codes = []
	with open(watch_list, 'rU') as csvfile:
		codes_reader = csv.reader(csvfile, dialect='excel')
		for code in codes_reader:
			codes.append(code[0])

	if not os.path.exists(path + "data/stock_data"):
		os.makedirs(path + "data/stock_data")
	
	if not os.listdir(path + "data/stock_data"):
		log_file.write(str(dt.datetime.now()) + " No data exists, performing full initialisation\n")
		init_all_codes(code, earliestDate, path, log_file)


	for code in codes:
		# check each code and see if the data is up to date
		file_name = path + "data/stock_data" + code + ".csv"
		if os.path.isfile(file_name):
			with open(file_name, 'r') as file:
				data_reader = csv.reader(file, dialect='excel')
			most_recent_date = data_reader[-1][0]
			# if the most recent data in the file is not up to date then we've got to wait until we've got the historical data on Sunday
			# so remove the code from the list
			if most_recent_date => todays_date - 1
		else:
			# remove code, wait til the end of the week

	return codes

def init_all_codes(code, earliestDate, path, log_file):
	log_file.write(str(dt.datetime.now()) + " Initalising historical data\n")
	stockPriceData = []
	earliestYear = 2000
	latestYear = dt.date.today().year() + 1
	dates = []
	for year in xrange(earliestYear, latestYear):
		for month in xrange(1,13):
			for day in xrange(1,32):
				dates.append(year * 10000 + month * 100 + day)

	for date in dates:
		file_name = "data/raw_data/" + str(date) + ".txt"
		if os.path.isfile(file_name):
			print "Reading data from " + str(date)
			with open(file_name, 'r') as file:
				data_reader = csv.reader(file, dialect='excel')
				for row in data_reader:
					if row[0] not in stockPriceData:
						stockPriceData[row[0]] = []
					stockPriceData[row[0]].append(row[1:])

	# save the data into a csv file
	# make the folder if it doesn't exist
	if not os.path.exists('data/stock_data/'):
		os.makedirs('data/stock_data/')
			
	for code in stockPriceData:
		file_name = "data/stock_data/" + code + ".csv"
		log_file.write(str(dt.datetime.now()) + " Writing data for " + code + "\n")
		with open(file_name, 'wb') as csvfile:
			writer = csv.writer(csvfile, delimiter=',')
			for row in stockPriceData[code]:
				writer.writerow(row)

def init_single_new_code(code, earliestDate, path, log_file):
	## Intended for adding a new code to the watchlist
	## This will be slow if doint the whole lot
	log_file.write(str(dt.datetime.now()) + " Initalising historical data for the new code " + code + "\n")
	stockPriceData = []
	earliestYear = 2000
	latestYear = dt.date.today().year() + 1
	dates = []
	for year in xrange(earliestYear, latestYear):
		for month in xrange(1,13):
			for day in xrange(1,32):
				dates.append(year * 10000 + month * 100 + day)

	for date in dates:
		file_name = "data/raw_data/" + str(date) + ".txt"
		if os.path.isfile(file_name):
			with open(file_name, 'r') as file:
				data_reader = csv.reader(file, dialect='excel')
				for row in data_reader:
					if row[0] == code:
						stockPriceData.append(row[1:])

			
	log_file.write(str(dt.datetime.now()) + " Writing price data\n")
	file_name = "data/stock_data/" + code + ".csv"
	with open(file_name, 'w+') as csvfile:
		writer = csv.writer(csvfile, delimiter=',')
		for row in stockPriceData:
			writer.writerow(row)

	log_file.write(str(dt.datetime.now()) + " Initialising technical analysis data\n")
	init_historical(code, earliestDate, path)

def init_historical(code, earliestDate, path):
	stockPriceData = []
	file_name = path + "data/stock_data/" + code + ".csv"
	with open(file_name, 'rU') as csvfile:
		data_reader = csv.reader(csvfile, dialect='excel')
		for data in data_reader:
			if data[0] > earliestDate:
				stockPriceData.append(data)

	rsi_path = path + "data/rsi_data/"
	if not os.path.exists(rsi_path):
		os.makedirs(rsi_path)
	
	bollinger_path = path + "data/bollinger_data/"
	if not os.path.exists(bollinger_path):
		os.makedirs(bollinger_path)

	period_short = 9
	period_long = 21
	ema921_path = path + "data/ema921_data/"
	if not os.path.exists(ema921_path):
		os.makedirs(ema921_path)

	period_short = 12
	period_long = 26
	period_signal = 9
	macd_path = path + "data/macd_data/"
	if not os.path.exists(macd_path):
		os.makedirs(macd_path)


	init_rsi(code, stockPriceData, rsi_path)
	init_bol(code, stockPriceData, bollinger_path)
	init_ema921(code, period_short, period_long, stockPriceData, ema921_path)
	init_macd(code, period_short, period_long, period_signal, stockPriceData, macd_path)

def init_rsi(code, stockPriceData, path):
	#RSI
	# Data is stored Date,Up_smma,Down_smma,RSI
	rsiData 		= []
	period 			= 14
	#use a 14 period modified moving average, so need to initialise
	x 				= [float(stockPriceData[n][4]) for n in range(0,len(stockPriceData))]
	up_days 		= [x[n]-x[n-1] if x[n]-x[n-1] >= 0 else 0 for n in range(1,len(x))]
	down_days 		= [x[n-1]-x[n] if x[n-1]-x[n] >= 0 else 0 for n in range(1,len(x))]

	up_smma 		= ema(period, up_days)
	down_smma 		= ema(period, down_days)

	rsData 			= [x/y for x, y in zip(up_smma,down_smma)]
	rsiData 		= [100 -100/(1 + x) for x in rsData]

	dates 			= [stockPriceData[n][0] for n in range(period-1,len(stockPriceData))]
	rsi_time_data 	= zip(dates, up_smma, down_smma,rsiData)
	
	print "Writing RSI data for " + code
	file_name 		= path + code + ".csv"
	write_init_data(file_name, rsi_time_data, [period])

def init_bol(code, stockPriceData, path):
	#Bollinger Bands

	bollingerData 		= {}
	period 				= 20
	K 					= 2

	bollingerData = []

	x 				= [float(stockPriceData[n][4]) for n in range(0,len(stockPriceData))]

	x_smma 			= ema(period, x)
	std_dev 		= [np.std(x[:period])]

	for i in xrange(period, len(x)):
		std_dev.append(np.std(x[(i+1-period):(i+1)]))

	upper 			= [x + K * y for x, y in zip(x_smma,std_dev)]
	lower 			= [x - K * y for x, y in zip(x_smma,std_dev)]

	dates = [stockPriceData[n][0] for n in range(period-1,len(stockPriceData))] #get the first element in each list
	bollinger_time_data = zip(dates, lower, x_smma, upper)

	print "Writing Bollinger data for " + code
	file_name 		= path + code + ".csv"
	write_init_data(file_name, bollinger_time_data, [period, K])

def init_ema(code, period, stockPriceData, path):
	# EMA for a given period

	emaData = []
	x 				= [float(stockPriceData[n][4]) for n in range(0,len(stockPriceData))]
	emaData 		= ema(period, x)

	dates 			= [stockPriceData[n][0] for n in range(period-1,len(stockPriceData))]
	ema_time_data 	= zip(dates, emaData)

	print "Writing " + str(period) + " period EMA data for " + code
	file_name 		= path + code + ".csv"
	write_init_data(file_name, ema_time_data, [period])

def init_ema921(code, period_short, period_long, stockPriceData, path):
	emaShortData = []
	emaLongData = []

	x 				= [float(stockPriceData[n][4]) for n in range(0,len(stockPriceData))]
	emaShortData 	= ema(period_short, x)
	emaLongData 	= ema(period_long, x)

	crossData 		= [x - y for x,y in zip(emaShortData[(period_long-period_short):], emaLongData)]

	dates 			= [stockPriceData[n][0] for n in range(period_long-1,len(stockPriceData))]
	ema921_time_data 	= zip(dates, emaShortData, emaLongData , crossData)

	print "Writing 9-21 EMA crossover data for " + code
	file_name 		= path + code + ".csv"
	write_init_data(file_name, ema921_time_data, [period_short, period_long])

def init_macd(code, period_short, period_long, period_signal, stockPriceData, path):
	emaShortData = []
	emaLongData = []
	emaSignalData = []
	
	x 				= [float(stockPriceData[n][4]) for n in range(0,len(stockPriceData))]
	emaShortData 	= ema(period_short, x)
	emaLongData 	= ema(period_long, x)
	emaSignalData	= ema(period_signal, x)

	short_start = period_long-period_short
	sig_start = period_long-period_signal

	macdLine 		= [x - y for x,y in zip(emaShortData[short_start:], emaLongData)]

	macdHist		= [x - y for x,y in zip(macdLine, emaSignalData[sig_start:])]

	dates 			= [stockPriceData[n][0] for n in range(period_long - 1,len(stockPriceData))]
	macd_time_data 	= zip(dates, emaShortData[short_start:], emaLongData, emaSignalData[sig_start:], macdLine, macdHist)

	print "Writing MACD data for " + code
	file_name 		= path + code + ".csv"
	write_init_data(file_name, macd_time_data, [period_short, period_long, period_signal])

def write_init_data(file_name, data, parameters):
	# parameters is a list of things like period K etc.
	# when reading back for updates, need to be aware of the order they are given
	with open(file_name, 'wb') as csvfile:
		writer 		= csv.writer(csvfile, delimiter=',')
		writer.writerow(parameters)
		for row in data:
			writer.writerow(row)

def ema(period, data):
	ema_data = [sum(data[:period])/period] # initialise with an SMA
	for i in xrange(period, len(data)):
		ema_data.append((ema_data[-1]*(period -1 ) + data[i])/period)

	return ema_data

