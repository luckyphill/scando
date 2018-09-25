import time
import datetime as dt
import os
import csv
import sys
import copy
import numpy as np
import os.path
import datetime as dt

import messages

from global_vars import *

def launch_procedure():
	# Runs once when program is started
	# This is designed to initialise everything from a very first startup,
	# and deal with new codes if they are added while the program is down
	
	todays_date = dt.date.today()

	codes = []
	if os.path.isfile(WATCH_FILE):
		with open(WATCH_FILE, 'rU') as csvfile:
			codes_reader = csv.reader(csvfile, dialect='excel')
			for code in codes_reader:
				codes.append(code[0])
	else:
		messages.popupmsg('ERROR', "You have no watch list. Make a file called 'watch_list.csv' and fill it with ASX codes first.")
		sys.exit()

	if not codes:
		messages.popupmsg('ERROR', "Your watch list is empty. Please add ASX codes, one to a line, all in capitals, then try again.")
		sys.exit()

	if not os.path.exists(STOCK_PATH):
		os.makedirs(STOCK_PATH)
	
	if not os.listdir(STOCK_PATH):
		LOG.write(str(dt.datetime.now()) + " No data exists, performing full initialisation\n")
		init_all_codes(codes)


	# On start up, we want to check if the stock data is up to date
	# If it's not then adding new EoD data will end up skipping previous days
	# In that case, remove the code from 'codes'
	# At the end of the week when the weekly update happens, everything will be fine and the code can be watched
	for code in codes:
		file_name = STOCK_PATH + code + ".csv"
		if os.path.isfile(file_name):
			with open(file_name, 'r') as file:
				data_reader = csv.reader(file, dialect='excel')
				data_list = list(data_reader)
			
			temp_date = data_list[-1][0]
			most_recent_date = dt.date(int(temp_date[:4]), int(temp_date[4:6]), int(temp_date[6:]))

			if most_recent_date < todays_date - dt.timedelta(1): # If too far behind
				if not (most_recent_date.weekday() == 4 and todays_date.weekday()==0): # Unless Friday and Monday
					#doesn't deal with special non trading days
					codes.remove(code)
		else:
			codes.remove(code)

	return codes

def init_all_codes(codes):
	LOG.write(str(dt.datetime.now()) + " Initalising historical data\n")
	stockPriceData = []
	latestYear = dt.date.today().year() + 1
	dates = []
	for year in xrange(EARLIEST_YEAR, latestYear):
		for month in xrange(1,13):
			for day in xrange(1,32):
				dates.append(year * 10000 + month * 100 + day)

	for date in dates:
		file_name = RAW_PATH + str(date) + ".txt"
		if os.path.isfile(file_name):
			print "Reading data from " + str(date)
			with open(file_name, 'r') as file:
				data_reader = csv.reader(file, dialect='excel')
				for row in data_reader:
					if row[0] not in stockPriceData and row[0] in codes:
						stockPriceData[row[0]] = []
					stockPriceData[row[0]].append(row[1:])

	# save the data into a csv file
	# make the folder if it doesn't exist
	if not os.path.exists(STOCK_PATH):
		os.makedirs(STOCK_PATH)
			
	for code in stockPriceData:
		file_name = STOCK_PATH + code + ".csv"
		LOG.write(str(dt.datetime.now()) + " Writing data for " + code + "\n")
		with open(file_name, 'wb') as csvfile:
			writer = csv.writer(csvfile, delimiter=',')
			for row in stockPriceData[code]:
				writer.writerow(row)

def init_single_new_code(code):
	## Intended for adding a new code to the watchlist
	## This will be slow if doing the whole lot
	LOG.write(str(dt.datetime.now()) + " Initalising historical data for the new code " + code + "\n")
	stockPriceData = []
	earliestYear = 2000
	latestYear = dt.date.today().year + 1
	dates = []
	for year in xrange(earliestYear, latestYear):
		for month in xrange(1,13):
			for day in xrange(1,32):
				dates.append(year * 10000 + month * 100 + day)

	for date in dates:
		file_name = RAW_PATH + str(date) + ".txt"
		if os.path.isfile(file_name):
			with open(file_name, 'r') as file:
				data_reader = csv.reader(file, dialect='excel')
				for row in data_reader:
					if row[0] == code:
						stockPriceData.append(row[1:])

			
	LOG.write(str(dt.datetime.now()) + " Writing price data\n")
	file_name = STOCK_PATH + code + ".csv"
	with open(file_name, 'w+') as csvfile:
		writer = csv.writer(csvfile, delimiter=',')
		for row in stockPriceData:
			writer.writerow(row)

	LOG.write(str(dt.datetime.now()) + " Initialising technical analysis data\n")
	init_historical(code)

def init_historical(code):
	stockPriceData = []
	file_name = path + STOCK_PATH + code + ".csv"
	with open(file_name, 'rU') as csvfile:
		data_reader = csv.reader(csvfile, dialect='excel')
		for data in data_reader:
			if data[0] > earliestDate:
				stockPriceData.append(data)

	RSI_PATH = path + "data/rsi_data/"
	if not os.path.exists(RSI_PATH):
		os.makedirs(RSI_PATH)
	
	BOL_PATH = path + "data/bollinger_data/"
	if not os.path.exists(BOL_PATH):
		os.makedirs(BOL_PATH)

	period_short = 9
	period_long = 21
	EMA921_PATH = path + "data/ema921_data/"
	if not os.path.exists(EMA921_PATH):
		os.makedirs(EMA921_PATH)

	period_short = 12
	period_long = 26
	period_signal = 9
	MACD_PATH = path + "data/macd_data/"
	if not os.path.exists(MACD_PATH):
		os.makedirs(MACD_PATH)


	init_rsi(code, stockPriceData)
	init_bol(code, stockPriceData)
	init_ema921(code, period_short, period_long, stockPriceData)
	init_macd(code, period_short, period_long, period_signal, stockPriceData)

def init_rsi(code, stockPriceData):
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
	file_name 		= RSI_PATH + code + ".csv"
	write_init_data(file_name, rsi_time_data, [period])

def init_bol(code, stockPriceData):
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
	file_name 		= BOL_PATH + code + ".csv"
	write_init_data(file_name, bollinger_time_data, [period, K])

def init_ema(code, period, stockPriceData):
	# EMA for a given period

	emaData = []
	x 				= [float(stockPriceData[n][4]) for n in range(0,len(stockPriceData))]
	emaData 		= ema(period, x)

	dates 			= [stockPriceData[n][0] for n in range(period-1,len(stockPriceData))]
	ema_time_data 	= zip(dates, emaData)

	print "Writing " + str(period) + " period EMA data for " + code
	file_name 		= path + code + ".csv"
	write_init_data(file_name, ema_time_data, [period])

def init_ema921(code, period_short, period_long, stockPriceData):
	emaShortData = []
	emaLongData = []

	x 				= [float(stockPriceData[n][4]) for n in range(0,len(stockPriceData))]
	emaShortData 	= ema(period_short, x)
	emaLongData 	= ema(period_long, x)

	crossData 		= [x - y for x,y in zip(emaShortData[(period_long-period_short):], emaLongData)]

	dates 			= [stockPriceData[n][0] for n in range(period_long-1,len(stockPriceData))]
	ema921_time_data 	= zip(dates, emaShortData, emaLongData , crossData)

	print "Writing 9-21 EMA crossover data for " + code
	file_name 		= EMA921_PATH + code + ".csv"
	write_init_data(file_name, ema921_time_data, [period_short, period_long])

def init_macd(code, period_short, period_long, period_signal, stockPriceData):
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
	file_name 		= MACD_PATH + code + ".csv"
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

