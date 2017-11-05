import time
import datetime as dt
import os
import csv
import sys
import copy
import numpy as np
import os.path


def init_from_historical(codes, earliestDate, path):
	# Initialises all data from historical records
	# This means all the technical analysis data
	if not os.path.exists(path + "stock_data/"):
		os.makedirs(path + "stock_data/")

	stockPriceData = {}
	for code in codes:
		stockPriceData[code] = []
		file_name = path + "stock_data/" + code + ".csv"
		with open(file_name, 'rU') as csvfile:
			data_reader = csv.reader(csvfile, dialect='excel')
			for data in data_reader:
				if data[0] > earliestDate:
					stockPriceData[code].append(data)

	init_rsi(codes, stockPriceData, path)
	init_bol(codes, stockPriceData, path)
	init_ema(codes, 9, stockPriceData, path)

def init_rsi(codes, stockPriceData, path):
	#RSI
	# Data is stored Date,Up_smma,Down_smma,RSI
	if not os.path.exists(path + "rsi_data/"):
		os.makedirs(path + "rsi_data/")

	rsiData 		= {}
	period 			= 14
	for code in stockPriceData:
		rsiData[code] 	= []
		#use a 14 period modified moving average, so need to initialise
		x 				= [float(stockPriceData[code][n][4]) for n in range(0,len(stockPriceData[code]))]
		up_days 		= [x[n]-x[n-1] if x[n]-x[n-1] >= 0 else 0 for n in range(1,len(x))]
		down_days 		= [x[n-1]-x[n] if x[n-1]-x[n] >= 0 else 0 for n in range(1,len(x))]

		up_smma 		= ema(period, up_days)
		down_smma 		= ema(period, down_days)

		rsData 			= [x/y for x, y in zip(up_smma,down_smma)]
		rsiData[code] 	= [100 -100/(1 + x) for x in rsData]

		rsi_time_data 	= zip([stockPriceData[code][n][0] for n in range(period,len(stockPriceData[code]))], up_smma, down_smma,rsiData[code])
		
		print "Writing RSI data for " + code
		file_name 		= path + "rsi_data/" + code + ".csv"
		write_init_data(file_name, rsi_time_data, [period])

def init_bol(codes, stockPriceData, path):
	#Bollinger Bands

	if not os.path.exists(path + "bollinger_data/"):
		os.makedirs(path + "bollinger_data/")

	bollingerData 		= {}
	period 				= 20
	K 					= 2

	for code in stockPriceData:
		bollingerData[code] = []

		x 				= [float(stockPriceData[code][n][4]) for n in range(0,len(stockPriceData[code]))]

		x_smma 			= ema(period, x)
		std_dev 		= [np.std(x[:period])]

		for i in xrange(period, len(x)):
			std_dev.append(np.std(x[(i+1-period):(i+1)]))

		upper 			= [x + K * y for x, y in zip(x_smma,std_dev)]
		lower 			= [x - K * y for x, y in zip(x_smma,std_dev)]

		bollinger_time_data = zip([stockPriceData[code][n][0] for n in range(period,len(stockPriceData[code]))], lower, x_smma, upper)
		print "Writing Bollinger data for " + code
		file_name 		= path + "bollinger_data/" + code + ".csv"
		write_init_data(file_name, bollinger_time_data, [period, K])

def init_ema(codes, period, stockPriceData, path):
	# EMA for a given period
	ema_path = path + "ema" + str(period) + "_data/"
	if not os.path.exists(ema_path):
		os.makedirs(ema_path)

	emaData = {}
	for code in stockPriceData:
		x 				= [float(stockPriceData[code][n][4]) for n in range(0,len(stockPriceData[code]))]
		emaData[code] 	= ema(period, x)

		ema_time_data 	= zip([stockPriceData[code][n][0] for n in range(period,len(stockPriceData[code]))], emaData[code])

		print "Writing " + str(period) + " period EMA data for " + code
		file_name 		= ema_path + code + ".csv"
		write_init_data(file_name, ema_time_data, [period])

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

