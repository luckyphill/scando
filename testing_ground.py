#!/usr/bin/python
import time
import datetime as dt
import csv
import os
import eod
import init


# Need to specify full paths for supervisord otherwise get errors
path 			= "/Users/manda/Shares/"
log_file 		= path + 'TEST_scando.log'
watch_list 		= path + 'Watch_list.csv'
lf 				= open(log_file, 'a')
num_days		= 10 #testing variable

# This is purely for testing new functions/process/data handling etc.
# SHOULD NOT BE USED FOR GA TRAINING!!!!!!!!
# All testing will be done with a phantom company with code TEST
# Data for TEST comes from IFL
# New data is poached from ANZ


codes = ['1AA'] # all testing done with code 1AA - this puts it at the top of the folder

init.init_from_historical(codes, path) # Takes the raw stock_data and turns it into technical data

#================================================================
# Make a place to "scan" from
file_scan = path + "stock_data/ANZ.csv"
with open(file_scan, 'r') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	scan_location = list(reader)
#================================================================


code = codes[0]
file_name = path + "stock_data/" + code + ".csv"

for days in xrange(num_days):
	#============================================================
	# a faux scan to give a new line of data in stock_data
	with open(file_name, 'a') as csvfile:
		writer = csv.writer(csvfile, delimiter=',')
		writer.writerow(scan_location[0])
		del scan_location[0]
	#============================================================

	eod.tech_update(codes, path, lf)

lf.close()

