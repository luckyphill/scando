# Signals catcher
import time
import datetime as dt
import os
import csv


def check_for_new_signals(codes, path):
	# Make a list of signal generating functions and loop through it
	dead_cat_path = path + 'data/stock_data/'
	rsi_path = path + 'data/rsi_data/'
	ema921_path = path + 'data/ema921_data/'

	signals_output = {} # A dictionary of signals for each stock
	for code in codes:
		#collect the data
		dead_cat_data = []
		with open(dead_cat_path + code + ".csv") as f:
			data_reader = csv.reader(f, delimiter=',')
			for line in data_reader:
				dead_cat_data.append(float(line[4]))

		rsi_data = []
		with open(rsi_path + code + ".csv") as f:
			data_reader = csv.reader(f, delimiter=',')
			for line in data_reader:
				if len(line) > 1: # First line has parameters
					rsi_data.append(float(line[3]))
		 
		ema921_data = []
		with open(ema921_path + code + ".csv") as f:
			data_reader = csv.reader(f, delimiter=',')
			for line in data_reader:
				ema921_data.append(float(line[1]))


		signals_list = [[dead_cat_bounce, dead_cat_data], [rsi_breaks, rsi_data], [ema921_crossover, ema921_data]]

		for signal in signals_list:
			signal_generator 	= signal[0]
			data 				= signal[1]

			result 				= signal_generator(code, data)
			
			if result:
				if code not in signals_output:
					signals_output[code] = []
				signals_output[code].append(result)


	return signals_output

def check_for_historical_signals(codes):
	# WILL NEED THIS FOR THE GENETIC ALGORITHM
	# Not useful right now

	signals_output = {}

	return signals_output

def dead_cat_bounce(code, price_data):
	abs_change = price_data[-1] - price_data[-2] # for a price drop this will be -ve
	rel_change = abs_change/price_data[-2]
	threshold  = 0.07

	if rel_change <  -threshold:
		return 'A significant drop has occurred for ' + code
	else:
		return False

def rsi_breaks(code, rsi_data):
	if rsi_data[-1] >=70 and rsi_data[-2]<70:
		return code + ' has broken above RSI of 70'
	elif rsi_data[-1] <=30 and rsi_data[-2]>30:
		return code + ' has broken below RSI of 30'
	else:
		return False

def ema921_crossover(code, ema921_data):
	if ema921_data[-1] > 0 and ema921_data[-2] < 0:
		return code + " has EMA 9-21 changed to POSITIVE"
	elif ema921_data[-1] < 0 and ema921_data[-2] > 0: 
		return code + " has EMA 9-21 changed to NEGATIVE"
	else:
		return False
