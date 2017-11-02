import csv
import operator
import copy
import os
import requests
from bs4 import BeautifulSoup

import webbrowser
import time
import datetime as dt

codes = []
with open("Watch_list.csv", 'rU') as csvfile:
	codes_reader = csv.reader(csvfile, dialect='excel')
	for code in codes_reader:
		codes.append(code[0])

bigcharts_url = 'http://bigcharts.marketwatch.com/quickchart/quickchart.asp?symb=AU%3A'
bigcharts_extra = '&insttype=Stock&freq=1&show=&time=8'

for code in codes:
	# page = home_url + code + page_detail
	page = bigcharts_url + code + bigcharts_extra
	print "\nRetrieving data for " + code
	print page
	response = requests.get(page)
	html = response.content
	soup = BeautifulSoup(html, "xml")
	table = soup.find('table', id="quote")
	temp_data = []
	for row in table.findAll('tr'):
		for cell in row.findAll('td'):
			temp_data.append(cell.text)
	
	# clean the data according to how the website presented it
	date = temp_data[1].split(' ')[0]
	open_p = temp_data[9].split('\n')[2]
	high = temp_data[10].split('\n')[2]
	low = temp_data[11].split('\n')[2]
	close = temp_data[7].split('\n')[2]
	vol = temp_data[12].split('\n')[2].replace(',', '')

	[month,day,year] = date.split('/')
	proper_date = year + month.zfill(2) + day.zfill(2)

	# all neatly tabulated ready for writing
	eod_data = [proper_date, open_p, high, low, close, vol]

	print "Writing data for " + code
	file_name = "stock_data/" + code + ".csv"
	with open(file_name, 'a') as csvfile:
		writer = csv.writer(csvfile, delimiter=',')
		writer.writerow(eod_data)

	print "Retrieval complete"

# Yahoo code: Note no date is supplied on page and data may not agree with ASX
# home_url = 'https://au.finance.yahoo.com/quote/'
# page_detail = '.AX'
# for code in codes:
# 	page = home_url + code + page_detail
# 	print page
# 	response = requests.get(page)
# 	html = response.content
# 	soup = BeautifulSoup(html, "xml")
	
# 	table = soup.find('tbody')
# 	temp_data = []
# 	for row in table.findAll('tr'):
# 		for cell in row.findAll('td'):
# 			temp_data.append(cell.text)

# 	div = soup.find_all("span", attrs={"data-reactid": "14"})
# 	for thing in div:
# 		temp_data.append(thing.text)

# 	proper_date = dt.date.today().strftime ("%Y%m%d")
# 	open_p = temp_data[3]
# 	high = temp_data[9].split("-")[1].strip()
# 	low = temp_data[9].split("-")[0].strip()
# 	close = temp_data[16]
# 	vol = temp_data[13]

# 	eod_data = [proper_date, open_p, high, low, close, vol]
# 	print eod_data




