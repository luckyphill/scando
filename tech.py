import csv
import sys
import copy

import numpy as np

import os.path

#calculate technical analysis data for all the data gathered
#this is intended for the first run, afterwards shorter updates will be used
#data is stored as Date,Open,High,Low,Close,Volume
earliestDate = 20000101

codes = []
with open("Watch_list.csv", 'rU') as csvfile:
	codes_reader = csv.reader(csvfile, dialect='excel')
	for code in codes_reader:
		codes.append(code[0])

stockPriceData = {}
for code in codes:
	# code = 'CBA'
	stockPriceData[code] = []
	file_name = "stock_data/" + code + ".csv"
	with open(file_name, 'rU') as csvfile:
		data_reader = csv.reader(csvfile, dialect='excel')
		for data in data_reader:
			if data[0] > earliestDate:
				stockPriceData[code].append(data)


#RSI
# Data is stored Date,Up_smma,Down_smma,RSI
rsiData 		= {}
period 			= 14
for code in stockPriceData:
	rsiData[code] 	= []
	#use a 14 period modified moving average, so need to initialise
	x 				= [float(stockPriceData[code][n][4]) for n in range(0,len(stockPriceData[code]))]
	up_days 		= [x[n]-x[n-1] if x[n]-x[n-1] >= 0 else 0 for n in range(1,len(x))]
	down_days 		= [x[n-1]-x[n] if x[n-1]-x[n] >= 0 else 0 for n in range(1,len(x))]

	up_smma 		= [sum(up_days[:period])/period]
	down_smma 		= [sum(down_days[:period])/period]
	
	for i in xrange(period, len(up_days)):
		up_smma.append((up_smma[-1]*(period -1 ) + up_days[i])/period)
		down_smma.append((down_smma[-1]*(period -1 ) + down_days[i])/period)


	rsData 			= [x/y for x, y in zip(up_smma,down_smma)]
	rsiData[code] 	= [100 -100/(1 + x) for x in rsData]

	rsi_time_data 	= zip([stockPriceData[code][n][0] for n in range(period,len(stockPriceData[code]))], up_smma, down_smma,rsiData[code])
	
	print "Writing RSI data for " + code
	file_name 		= "rsi_data/" + code + ".csv"
	
	with open(file_name, 'wb') as csvfile:
		writer 			= csv.writer(csvfile, delimiter=',')
		writer.writerow([period])
		for row in rsi_time_data:
			writer.writerow(row)


#Bollinger Bands
bollingerData 		= {}
period 				= 20
K 					= 2

for code in stockPriceData:
	bollingerData[code] = []

	x 				= [float(stockPriceData[code][n][4]) for n in range(0,len(stockPriceData[code]))]

	x_smma 			= [sum(x[:period])/period]
	std_dev 		= [np.std(x[:period])]

	for i in xrange(period, len(x)):
		x_smma.append((x_smma[-1]*(period -1 ) + x[i])/period)
		std_dev.append(np.std(x[(i+1-period):(i+1)]))

	upper 			= [x + K * y for x, y in zip(x_smma,std_dev)]
	lower 			= [x - K * y for x, y in zip(x_smma,std_dev)]

	bollinger_time_data = zip([stockPriceData[code][n][0] for n in range(period,len(stockPriceData[code]))], lower, x_smma, upper)
	print "Writing Bollinger data for " + code
	file_name 		= "bollinger_data/" + code + ".csv"
	
	with open(file_name, 'wb') as csvfile:
		writer 		= csv.writer(csvfile, delimiter=',')
		writer.writerow([period])
		writer.writerow([K])
		for row in bollinger_time_data:
			writer.writerow(row)
