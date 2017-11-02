import csv
import sys
import copy

codes = []
with open("20171001-asx200.csv", 'rU') as csvfile:
	games_reader = csv.reader(csvfile, dialect='excel')
	for game in games_reader:
		codes.append(game[0])
		print game[0]

del codes[0:2]
with open("Watch_list.csv", 'wb') as file:
	for code in codes:
		file.write(code)
		file.write("\n")