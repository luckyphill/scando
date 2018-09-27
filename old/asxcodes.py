import csv
import sys
import copy
import os
import numpy as np

all_codes = []

latest_file = os.listdir('../data/raw_data/')[0]
for file in os.listdir('../data/raw_data/')[1:]:
	if file > latest_file:
		latest_file = file

path_to_latest_file = "../data/raw_data/" + latest_file

with open(path_to_latest_file, 'rU') as csvfile:
	code_reader = csv.reader(csvfile, dialect='excel')
	for code in code_reader:
		all_codes.append(code[0])
		print code[0]

print len(all_codes)

# Take the last 100 days worth of trading data and find the average volume for each code
volume_100_days = {}
value_100_days = {}
for file in os.listdir('../data/raw_data/')[-100:]:
	path = "../data/raw_data/" + file
	with open(path,'r') as csvfile:
		raw_data_reader = csv.reader(csvfile)
		for data in raw_data_reader:
			if data[0] in all_codes:
				if data[0] not in volume_100_days:
					volume_100_days[data[0]] = []
					value_100_days[data[0]] = []
				volume_100_days[data[0]].append(int(data[-1]))
				value_100_days[data[0]].append( round(float(data[-1])*float(data[4]),2) )


avg_value_100_days = {}
potential_watch_list = []

cut_off_limit = 500000

for code in all_codes:
	avg_value_100_days[code] = np.mean(value_100_days[code])
	if avg_value_100_days[code] > cut_off_limit:
		potential_watch_list.append(code)

print len(potential_watch_list)


# del all_codes[0:2]
# with open("Watch_list.csv", 'wb') as file:
# 	for code in all_codes:
# 		file.write(code)
# 		file.write("\n")