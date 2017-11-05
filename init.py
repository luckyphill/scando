import time
import datetime as dt
import os
import csv
import sys
import copy
import numpy as np
import os.path


def init_historical(code, earliestDate, path):
	stockPriceData = []
	file_name = path + "stock_data/" + code + ".csv"
	with open(file_name, 'rU') as csvfile:
		data_reader = csv.reader(csvfile, dialect='excel')
		for data in data_reader:
			if data[0] > earliestDate:
				stockPriceData.append(data)

	rsi_path = path + "rsi_data/"
	if not os.path.exists(rsi_path):
		os.makedirs(rsi_path)
	
	bollinger_path = path + "bollinger_data/"
	if not os.path.exists(bollinger_path):
		os.makedirs(bollinger_path)
	
	period = 9
	ema_path = path + "ema" + str(period) + "_data/"
	if not os.path.exists(ema_path):
		os.makedirs(ema_path)

	period_short = 9
	period_long = 21
	macd_path = path + "macd" + str(period_short) + "-" + str(period_long) + "_data/"
	if not os.path.exists(macd_path):
		os.makedirs(macd_path)

	init_rsi(code, stockPriceData, rsi_path)
	init_bol(code, stockPriceData, bollinger_path)
	init_ema(code, period, stockPriceData, ema_path)
	init_macd(code, period_short, period_long, stockPriceData, macd_path)

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

	rsi_time_data 	= zip([stockPriceData[n][0] for n in range(period,len(stockPriceData))], up_smma, down_smma,rsiData)
	
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

	bollinger_time_data = zip([stockPriceData[n][0] for n in range(period,len(stockPriceData))], lower, x_smma, upper)
	print "Writing Bollinger data for " + code
	file_name 		= path + code + ".csv"
	write_init_data(file_name, bollinger_time_data, [period, K])

def init_ema(code, period, stockPriceData, path):
	# EMA for a given period

	emaData = []
	x 				= [float(stockPriceData[n][4]) for n in range(0,len(stockPriceData))]
	emaData 		= ema(period, x)

	ema_time_data 	= zip([stockPriceData[n][0] for n in range(period,len(stockPriceData))], emaData)

	print "Writing " + str(period) + " period EMA data for " + code
	file_name 		= path + code + ".csv"
	write_init_data(file_name, ema_time_data, [period])

def init_macd(code, period_short, period_long, stockPriceData, path):
	emaShortData = []
	emaLongData = []
	x 				= [float(stockPriceData[n][4]) for n in range(0,len(stockPriceData))]
	emaShortData 	= ema(period_short, x)
	emaLongData 	= ema(period_long, x)

	macdData 		= [x - y for x,y in zip(emaShortData[(period_long-period_short):], emaLongData)]

	macd_time_data 	= zip([stockPriceData[n][0] for n in range(period_long,len(stockPriceData))], macdData)

	print "Writing " + str(period_short) + "-" + str(period_long) + " period MACD data for " + code
	file_name 		= path + code + ".csv"
	write_init_data(file_name, macd_time_data, [period_short, period_long])

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

