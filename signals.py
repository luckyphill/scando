# Signals catcher
import time
import datetime as dt
import os
import csv

from global_vars import *


def check_for_new_signals(codes):
	# Make a list of signal generating functions and loop through it

	signals_output = {} # A dictionary of signals for each stock
	for code in codes:
		LOG.write(str(dt.datetime.now()) + " Checking for signals from " + code + "\n")
		#collect the data
		previous_close_data = []
		with open(STOCK_PATH + code + ".csv") as f:
			data_reader = csv.reader(f, delimiter=',')
			for line in data_reader:
				previous_close_data.append(float(line[4]))

		rsi_data = []
		with open(RSI_PATH + code + ".csv") as f:
			data_reader = csv.reader(f, delimiter=',')
			for line in data_reader:
				if len(line) > 1: # First line has parameters
					rsi_data.append(float(line[3]))
		 
		ema921_data = []
		with open(EMA921_PATH + code + ".csv") as f:
			data_reader = csv.reader(f, delimiter=',')
			for line in data_reader:
				ema921_data.append(float(line[1]))


		signals_list = [[dead_cat_bounce, previous_close_data], [period_highs, previous_close_data], [rsi_breaks, rsi_data], [ema921_crossover, ema921_data]]

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

def period_highs(code, price_data):
	## A simple signal that tells if the stock has reached a 1 week, 1 month, 6 month or 1 year high
	last_close = price_data[-1]
	days_highest = 0
	for price in reversed(price_data[:-1]):
		if last_close > price:
			days_highest = days_highest +1
		else:
			break

	if days_highest > 200:
		return code + ' has hit a 200 day high'

	if days_highest > 100:
		return code + ' has hit a 100 day high'

	if days_highest > 50:
		return code + ' has hit a 50 day high'

	if days_highest > 25:
		return code + ' has hit a 25 day high'

	return False