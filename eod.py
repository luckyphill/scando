import csv
import requests
from bs4 import BeautifulSoup

import time
import datetime as dt
import numpy as np
import os
import urllib
import zipfile
import shutil

import signals
import init
import messages

from global_vars import *


def scan(codes):
	# Scans the website http://bigcharts.marketwatch.com for the latest EoD data

	for code in codes:
		LOG.write(str(dt.datetime.now()) + " Checking current data for " + code + "\n")
		
		file_name = STOCK_PATH + code + ".csv"

		with open(file_name, 'r') as csvfile:
			reader = csv.reader(csvfile, delimiter=',')
			reader_list = list(reader)
			last_entry = reader_list[-1]

		if last_entry[0] == dt.date.today().strftime ("%Y%m%d"): # make sure we haven't already got today's data
			
			LOG.write(str(dt.datetime.now()) + " Data appears to be up to date.\n")
		
		elif last_entry[0] < dt.date.today().strftime ("%Y%m%d"): # make sure we're adding the next date

			try:
				LOG.write(str(dt.datetime.now()) + " Retrieving data\n")
				page = URL_EOD + code + URL_EOD_END
				LOG.write(str(dt.datetime.now()) + " " + page + "\n")
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

				# write the data to file
				LOG.write(str(dt.datetime.now()) + " Writing data\n")
				with open(file_name, 'a') as csvfile:
					writer = csv.writer(csvfile, delimiter=',')
					writer.writerow(eod_data)

				LOG.write(str(dt.datetime.now()) + " Retrieval complete\n")
			except:
				LOG.write(str(dt.datetime.now()) + " There was an issue retrieving EoD data for " + code +"\n")

		else:

			LOG.write(str(dt.datetime.now()) + " Something has gone wrong, we appear to be adding old data.\n")

def tech_update(codes):
	# Updates the technical analysis data files given the new data
	# In this function we are assuming that stock data is complete and accurate

	for code in codes:
		
		rsi_file = RSI_PATH + code + ".csv"
		bollinger_file = BOL_PATH + code + ".csv"
		ema921_file = EMA921_PATH + code + ".csv"
		quote_file = STOCK_PATH + code + ".csv"

		with open(quote_file, 'r') as f:
			quote_reader = csv.reader(f, delimiter=',')
			quote_list 	= list(quote_reader)
			

		# Make a dictionary of function pointers and files and pass this into the update function
		analysis_list = [['RSI', rsi_new_data, rsi_file],['Bollinger Bands', bol_new_data, bollinger_file], ['9-21 Period EMA Cross over', ema921_new_data, ema921_file]]
		for analysis_type in analysis_list:
			
			analysis_name = analysis_type[0]
			analysis_function = analysis_type[1]
			analysis_file = analysis_type[2]

			update(code, quote_list, analysis_name, analysis_function, analysis_file)
		
	# for each code, we want to look at the latest data and update the technical ananlysis files
	# at the moment we have RSI and Bollinger bands

def clean_log():
	# This is the only function that is allowed to modify a global variable
	# Ought to investigate best practive for something like this
	global LOG
	LOG.write(str(dt.datetime.now()) + " Cleaning logs\n")
	LOG.close()
	if (os.path.getsize(LOG_FILE) > LOG_SIZE_LIMIT):
		with open(LOG_FILE,'r') as lf, open("temp.log" ,"w") as out:
			#only write the last half
			lf.seek(int(LOG_SIZE_LIMIT/2))
			for line in lf:
				out.write(line)

		os.remove(LOG_FILE)
		os.rename("temp.log", LOG_FILE)
	LOG = open(LOG_FILE,'a+',BUFFER_SIZE) 

def get_codes():
	# Takes a direct path to the watch_list file
	codes = []
	with open(WATCH_FILE, 'rU') as csvfile:
		codes_reader = csv.reader(csvfile, dialect='excel')
		for code in codes_reader:
			codes.append(code[0])
	return codes

def update(code, quote_list, analysis_name, analysis_function, analysis_file):
	# Update data for a given stock and a given analysis approach
	latest_quote_date = quote_list[-1][0]
	LOG.write(str(dt.datetime.now()) + " Updating " + analysis_name + " data for " + code + "\n")
	
	with open(analysis_file, 'r') as f:
		analysis_reader = csv.reader(f, delimiter=',')
		analysis_prev_data = list(analysis_reader)
	
	latest_analysis_date = analysis_prev_data[-1][0]

	if  latest_quote_date == latest_analysis_date:
		LOG.write(str(dt.datetime.now()) + " Data appears to be up to date\n")
	else:

		new_data = analysis_function(quote_list, analysis_prev_data)

		LOG.write(str(dt.datetime.now()) + " Writing data\n")
		with open(analysis_file, 'a') as f:
			analysis_writer = csv.writer(f, delimiter=',')
			analysis_writer.writerow(new_data)

def rsi_new_data(quote_list, rsi_prev_data):
	latest_quote_date 	= quote_list[-1][0]
	period 				= float(rsi_prev_data[0][0])
	prev_data			= [float(i) for i in rsi_prev_data[-1]]

	x 					= [[float(i) for i in row] for row in quote_list[-2:]] # The last two rows. Only interested in the last entry to make up and down
	up					= x[1][4] - x[0][4] if x[1][4] - x[0][4] >= 0 else 0
	down 				= x[0][4] - x[1][4] if x[0][4] - x[1][4] >= 0 else 0
	up_smma				= (prev_data[1]*(period -1 ) + up)/period
	down_smma			= (prev_data[2]*(period -1 ) + up)/period
	rs 					= up_smma/down_smma
	rsi 				= 100 -100/(1 + rs)

	return [latest_quote_date, up_smma, down_smma, rsi]

def bol_new_data(quote_list, bol_prev_data):
	latest_quote_date 	= quote_list[-1][0]
	period 				= int(bol_prev_data[0][0])
	K					= int(bol_prev_data[0][1])

	x 					= [[float(i) for i in row] for row in quote_list[-period:]]
	prev_data			= [float(i) for i in bol_prev_data[-1]]
	smma 				= (prev_data[2]*(period -1 ) + x[-1][4])/period
	std_dev 			= np.std([x[i][4] for i in range(0,period)])

	upper 				= smma + K * std_dev
	lower 				= smma - K * std_dev

	return [latest_quote_date, lower, smma, upper]

def ema_new_data(quote_list, ema_prev_data):
	latest_quote_date	= quote_list[-1][0]
	period 				= float(ema_prev_data[0][0])
	prev_data			= [float(i) for i in ema_prev_data[-1]]

	ema					= (prev_data[1]*(period - 1) + float(quote_list[-1][4]))/period

	return [latest_quote_date, ema]

def macd_new_data(quote_list, macd_prev_data):
	# make two emas with 12 and 26 and take the difference
	# then take a signal line
	latest_quote_date	= quote_list[-1][0]
	period_short		= float(macd_prev_data[0][0])
	period_long			= float(macd_prev_data[0][1])
	period_signal		= float(macd_prev_data[0][2])
	
	prev_data			= [float(i) for i in macd_prev_data[-1]]

	ema_short			= (prev_data[1]*(period_short - 1) + float(quote_list[-1][4]))/period_short
	ema_long			= (prev_data[2]*(period_long - 1) + float(quote_list[-1][4]))/period_long
	ema_signal			= (prev_data[2]*(period_signal - 1) + float(quote_list[-1][4]))/period_signal

	macd_line			= ema_short - ema_long
	macd_hist			= macd_line - ema_signal

	return [latest_quote_date, ema_short, ema_long, ema_signal, macd_line, macd_hist]

def ema921_new_data(quote_list, ema921_prev_data):
	# make two emas with 9 and 21 and take the difference
	latest_quote_date	= quote_list[-1][0]
	period_short		= float(ema921_prev_data[0][0])
	period_long			= float(ema921_prev_data[0][1])
	
	prev_data			= [float(i) for i in ema921_prev_data[-1]]

	ema921_short		= (prev_data[1]*(period_short - 1) + float(quote_list[-1][4]))/period_short
	ema921_long			= (prev_data[2]*(period_long - 1) + float(quote_list[-1][4]))/period_long

	cross_hist			= ema921_short - ema921_long

	return [latest_quote_date, ema921_short, ema921_long, cross_hist]

def get_historical():
	# This is only meant to run on a Sunday
	date = dt.date.today()
	date = date - dt.timedelta(2)
	file_name = 'week' + date.strftime("%Y%m%d") + ".zip"
	dl_location = URL_HISTORICAL + file_name
	file_location = 'data/zip_data/' + file_name
	
	if not os.path.exists('data/zip_data/'):
		os.makedirs('data/zip_data/')

	try:
		LOG.write(str(dt.datetime.now()) + " Downloading historical data for week ending " + date.strftime("%Y%m%d" + "\n")) 
		urllib.urlretrieve (dl_location, file_location)

		zip_ref = zipfile.ZipFile(file_location, 'r')
		extract_location = 'data/raw_data/'
		if not os.path.exists(extract_location):
			os.makedirs(extract_location)

		LOG.write(str(dt.datetime.now()) + " Unzipping new data\n")
		zip_ref.extractall(extract_location)
		zip_ref.close()

		root = 'data/raw_data/'
		subd = 'week' + date.strftime("%Y%m%d")
		for filename in os.listdir(os.path.join(root, subd)):
		    shutil.move(os.path.join(root, subd, filename), os.path.join(root, filename))
		os.rmdir(root + subd)
		LOG.write(str(dt.datetime.now()) + "Download successful\n")

	except:
		LOG.write(str(dt.datetime.now()) + "Download failed, try manually downloading\n")
		messages.popupmsg('Auto Download', "Auto Download didn't work mate, try it manually " +  dl_location)

def check_for_watch_list_additions(old_codes):
	# Checks for changes to the watchlist and initialises any new codes
	# Can delete unwanted data, but doesn't do it yet
	new_codes = get_codes()
	remove_list = []
	add_list = []
	for code in old_codes:
		if code not in new_codes:
			remove_list.append(code)

	for code in new_codes:
		if code not in old_codes:
			add_list.append(code)

	for code in add_list:
		init.init_single_new_code(code)

	return new_codes

def check_for_watch_list_removals(old_codes):
	# Checks for changes to the watchlist and initialises any new codes
	# Can delete unwanted data, but doesn't do it yet
	watch_list = get_codes()
	remove_list = []
	for code in old_codes:
		if code not in watch_list:
			remove_list.append(code)

	for code in remove_list:
		if code in old_codes:
			LOG.write(str(dt.datetime.now()) + " No longer collecting EoD data for " + code + "\n")
			old_codes.remove(code)
	
	return old_codes

def notify_of_signals(codes):
	all_signals = signals.check_for_new_signals(codes)
	for code in all_signals:
		signals_for_code = all_signals[code]
		signal_message = ''
		for signal in signals_for_code:
			LOG_SIG.write(str(dt.datetime.now()) + " " + signal + "\n")
			signal_message = signal_message + "\n" + signal
		
		messages.popupmsg(code, signal_message)

def check_radar(old_codes):
	## Checks once a week to see if there are any stocks that have moved past the
	## minimum trading value threshold

	## First, make a list of all the companies trading according to asxhistoricaldata.com
	all_codes = []

	latest_file = os.listdir(RAW_PATH)[0]
	for file in os.listdir(RAW_PATH)[1:]:
		if file > latest_file:
			latest_file = file

	path_to_latest_file = RAW_PATH + latest_file

	with open(path_to_latest_file, 'rU') as csvfile:
		code_reader = csv.reader(csvfile, dialect='excel')
		for code in code_reader:
			all_codes.append(code[0])

	## We now have a list of all the codes trading as of the last day's trade

	## Now we want to calculate the 100 day average trading value

	value_100_days = {}
	## Read each file for the last 100 days, and store the traded value
	for file in os.listdir(RAW_PATH)[-100:]:
		path = RAW_PATH + file
		
		with open(path,'r') as csvfile:
			raw_data_reader = csv.reader(csvfile)
			
			for data in raw_data_reader:
				if data[0] in all_codes:
					if data[0] not in volume_100_days:
						value_100_days[data[0]] = []
					## Traded value taken to be the volume * low price to give a conservative estimate
					value_100_days[data[0]].append(  round( float(data[-1])*float(data[4]), 2 )  )

	## Now calculate the average and populate the new watchlist
	avg_value_100_days = {}
	codes_above_limit = []
	old_codes_below_limit = []

	for code in all_codes:
		avg_value_100_days[code] = np.mean(value_100_days[code])
		## Grab codes peaking over the value cut-off limit
		if avg_value_100_days[code] > VALUE_CUTOFF:
			if code not in old_codes:
				codes_above_limit.append(code)
		## If a code drops below 90% of the limit, get rid of it, 
		if avg_value_100_days[code] < 0.9 * VALUE_CUTOFF:
			if code in old_codes:
				old_codes_below_limit.append(code)

	if codes_above_limit:
		for code in codes_above_limit:
			messages.popupmsg(code, code + ' has pushed through the 100 day average value cut-off. Adding to watch list.')
			

	if old_codes_below_limit:
		for code in old_codes_below_limit:
			messages.popupmsg(code, code + ' has dropped below 90\% of the 100 day average value cut-off. Removing from watch list.')


	return codes_above_limit



#=============================================================================
# Old code that I'm not comfortable enough yet to delete
#=============================================================================

# Yahoo code: Note no date is supplied on page and data may not agree with ASX
# home_url = 'https://au.finance.yahoo.com/quote/'
# page_detail = '.AX'
# for code in codes:
# 	page = home_url + code + page_detail
# 	LOG.write(str(dt.datetime.now()) + p age
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


