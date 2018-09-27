import time
import datetime as dt
import os
import csv
import sys
import copy
import numpy as np
import os.path
import datetime as dt

PATH = "/Users/phillipbrown/scando/"
DATA_PATH = PATH + "data/"
LOG_PATH = PATH + "logs/"
RAW_PATH = DATA_PATH + "raw_data/"
ZIP_PATH = DATA_PATH + "zip_data/"
STOCK_PATH = "/Users/phillipbrown/Documents/MATLAB/scando/stock_data/"


codes = []

latest_file = os.listdir('/data/raw_data/')[0]
for file in os.listdir('/data/raw_data/')[1:]:
	if file > latest_file:
		latest_file = file

path_to_latest_file = "/data/raw_data/" + latest_file

with open(path_to_latest_file, 'rU') as csvfile:
	code_reader = csv.reader(csvfile, dialect='excel')
	for code in code_reader:
		codes.append(code[0])
		print code[0]

print len(codes)

stockPriceData = {}

dates = []
for year in xrange(2000,2019):
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
				if row[0] in codes:
					stockPriceData[row[0]].append(row[1:])

# save the data into a csv file
# make the folder if it doesn't exist
if not os.path.exists(STOCK_PATH):
	os.makedirs(STOCK_PATH)
		
for code in codes:
	file_name = STOCK_PATH + code + ".csv"
	with open(file_name, 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter=',')
		for row in stockPriceData[code]:
			writer.writerow(row)