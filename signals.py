# Signals catcher
import time
import datetime as dt
import os


path 		= "/Users/manda/Shares/"
siglog 		= path + 'siglog.log'

def check_for_signals():
	# Make a list of signal generating functions and loop through it
	return 0


def dead_cat_bounce(code, price_data):
	abs_change = price_data[-1] - price_data[-2] # for a price drop this will be -ve
	rel_change = abs_change/price_data[-2]
	threshold  = 0.1

	if rel_change <  -threshold:
		return 'A significant drop has occurred for ' + code
	else:
		return False

def rsi_breaks(code, price_data):
	if price_data[-1] >=70 and price_data[-2]<70:
		return code + ' has broken above RSI of 70'
	elif price_data[-1] <=30 and price_data[-2]>30:
		return code + ' has broken below RSI of 30'
