import csv
import sys
import copy
import init
import numpy as np

import os.path

#calculate technical analysis data for all the data gathered
#this is intended for the first run, afterwards shorter updates will be used
#data is stored as Date,Open,High,Low,Close,Volume
earliestDate 	= 20000101
path 			= "/Users/phillipbrown/scando/"
watch_list = path + "Watch_list.csv"


codes = []
with open(watch_list, 'rU') as csvfile:
	codes_reader = csv.reader(csvfile, dialect='excel')
	for code in codes_reader:
		codes.append(code[0])
for code in codes:
	init.init_historical(code, earliestDate, path)