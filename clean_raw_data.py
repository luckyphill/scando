import csv
import sys
import copy

import os.path


codes = []
with open("Watch_list.csv", 'rU') as csvfile:
	codes_reader = csv.reader(csvfile, dialect='excel')
	for code in codes_reader:
		codes.append(code[0])

# create a list of file names, if the file exists, open it and read the data into the data structure

stockPriceData = {}
earliestYear = 2000
latestYear = 2018
dates = []
for year in xrange(earliestYear, latestYear):
	for month in xrange(1,13):
		for day in xrange(1,32):
			dates.append(year * 10000 + month * 100 + day)

for date in dates:
	file_name = "raw_data/" + str(date) + ".txt"
	if os.path.isfile(file_name):
		print "Reading data from " + str(date)
		with open(file_name, 'r') as file:
			data_reader = csv.reader(file, dialect='excel')
			for row in data_reader:
				if row[0] not in stockPriceData:
					# print row[0] + " is new"
					stockPriceData[row[0]] = []
				stockPriceData[row[0]].append(row[1:])
	else:
		print "No data for " + str(date)

# save the data into a csv file

for company in stockPriceData:
	print "Writing data for " + company
	file_name = "stock_data/" + company + ".csv"
	with open(file_name, 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter=',')
		for row in stockPriceData[company]:
			writer.writerow(row)

