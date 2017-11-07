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
import Tkinter as tk
import ttk

import signals
import init


NORM_FONT 		= ("Verdana", 10) # Font for popups


def scan(codes, path, log_file):
	# Scans the website http://bigcharts.marketwatch.com for the latest EoD data

	bigcharts_url = 'http://bigcharts.marketwatch.com/quickchart/quickchart.asp?symb=AU%3A'
	bigcharts_extra = '&insttype=Stock&freq=1&show=&time=8'

	for code in codes:
		log_file.write(str(dt.datetime.now()) + " Checking current data for " + code + "\n")
		
		file_name = path + "data/stock_data/" + code + ".csv"

		with open(file_name, 'r') as csvfile:
			reader = csv.reader(csvfile, delimiter=',')
			reader_list = list(reader)
			last_entry = reader_list[-1]

		if last_entry[0] == dt.date.today().strftime ("%Y%m%d"): # make sure we haven't already got today's data
			
			log_file.write(str(dt.datetime.now()) + " Data appears to be up to date.\n")
		
		elif last_entry[0] < dt.date.today().strftime ("%Y%m%d"): # make sure we're adding the next date

			try:
				log_file.write(str(dt.datetime.now()) + " Retrieving data\n")
				page = bigcharts_url + code + bigcharts_extra
				log_file.write(str(dt.datetime.now()) + " " + page + "\n")
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
				log_file.write(str(dt.datetime.now()) + " Writing data\n")
				with open(file_name, 'a') as csvfile:
					writer = csv.writer(csvfile, delimiter=',')
					writer.writerow(eod_data)

				log_file.write(str(dt.datetime.now()) + " Retrieval complete\n")
			except:
				log_file.write(str(dt.datetime.now()) + " There was an issue retrieving EoD data for " + code +"\n")

		else:

			log_file.write(str(dt.datetime.now()) + " Something has gone wrong, we appear to be adding old data.\n")

def tech_update(codes, path, log_file):
	# Updates the technical analysis data files given the new data
	# In this function we are assuming that stock data is complete and accurate

	for code in codes:
		
		rsi_file = path + "data/rsi_data/" + code + ".csv"
		bollinger_file = path + "data/bollinger_data/" + code + ".csv"
		ema921_file = path + "data/ema921_data/" + code + ".csv"
		quote_file = path + "data/stock_data/" + code + ".csv"

		with open(quote_file, 'r') as f:
			quote_reader = csv.reader(f, delimiter=',')
			quote_list 	= list(quote_reader)
			

		# Make a dictionary of function pointers and files and pass this into the update function
		analysis_list = [['RSI', rsi_new_data, rsi_file],['Bollinger Bands', bol_new_data, bollinger_file], ['9-21 Period EMA Cross over', ema921_new_data, ema921_file]]
		for analysis_type in analysis_list:
			
			analysis_name = analysis_type[0]
			analysis_function = analysis_type[1]
			analysis_file = analysis_type[2]

			update(code, quote_list, analysis_name, analysis_function, analysis_file, log_file)
		
	# for each code, we want to look at the latest data and update the technical ananlysis files
	# at the moment we have RSI and Bollinger bands

def clean_log(log_file, log_size_limit):
	if (os.path.getsize(log_file) > log_size_limit):
		
		with open(log_file,'r') as lf, open("temp.log" ,"w") as out:
			#only write the last half
			lf.seek(int(log_size_limit/2))
			for line in lf:
				out.write(line)

		os.remove(log_file)
		os.rename("temp.log", log_file)

def get_codes(watch_list):
	# Takes a direct path to the watch_list file
	codes = []
	with open(watch_list, 'rU') as csvfile:
		codes_reader = csv.reader(csvfile, dialect='excel')
		for code in codes_reader:
			codes.append(code[0])
	return codes

def update(code, quote_list, analysis_name, analysis_function, analysis_file, log_file):
	# Update data for a given stock and a given analysis approach
	latest_quote_date = quote_list[-1][0]
	log_file.write(str(dt.datetime.now()) + " Updating " + analysis_name + " data for " + code + "\n")
	
	with open(analysis_file, 'r') as f:
		analysis_reader = csv.reader(f, delimiter=',')
		analysis_prev_data = list(analysis_reader)
	
	latest_analysis_date = analysis_prev_data[-1][0]

	if  latest_quote_date == latest_analysis_date:
		log_file.write(str(dt.datetime.now()) + " Data appears to be up to date\n")
	else:

		new_data = analysis_function(quote_list, analysis_prev_data)

		log_file.write(str(dt.datetime.now()) + " Writing data\n")
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

def get_historical(log_file):
	data_page = 'https://www.asxhistoricaldata.com/data/'
	date = dt.date.today()#.strftime("%Y%m%d")
	# We're going to assume it's a sunday
	date = date - dt.timedelta(2)
	file_name = 'week' + date.strftime("%Y%m%d") + ".zip"
	dl_location = data_page + file_name
	file_location = 'data/zip_data/' + file_name
	
	if not os.path.exists('data/zip_data/'):
		os.makedirs('data/zip_data/')

	try:
		log_file.write(str(dt.datetime.now()) + "Downloading historical data for week ending " + date.strftime("%Y%m%d")) 
		urllib.urlretrieve (dl_location, file_location)

		zip_ref = zipfile.ZipFile(file_location, 'r')
		extract_location = 'data/raw_data/'
		if not os.path.exists(extract_location):
			os.makedirs(extract_location)

		log_file.write(str(dt.datetime.now()) + "Unzipping new data")
		zip_ref.extractall(extract_location)
		zip_ref.close()

		root = 'data/raw_data/'
		subd = 'week' + date.strftime("%Y%m%d")
		for filename in os.listdir(os.path.join(root, subd)):
		    shutil.move(os.path.join(root, subd, filename), os.path.join(root, filename))
		os.rmdir(root + subd)
		log_file.write(str(dt.datetime.now()) + "Download successful")

	except:
		log_file.write(str(dt.datetime.now()) + "Download failed, try manually downloading")
		popupmsg('Auto Download', "Auto Download didn't work mate, try it manually " +  dl_location)

def check_for_watch_list_change(old_codes, watch_list, earliestDate, path, log_file):
	# Checks for changes to the watchlist and initialises any new codes
	# Can delete unwanted data, but doesn't do it yet
	new_codes = get_codes(watch_list)
	remove_list = []
	add_list = []
	for code in old_codes:
		if code not in new_codes:
			remove_list.append(code)

	for code in new_codes:
		if code not in old_codes:
			add_list.append(code)

	for code in add_list:
		init.init_single_new_code(code, earliestDate, path, log_file):

	return new_codes

def notify_of_signals(codes, path, sig_log_file):
	all_signals = signals.check_for_new_signals(codes, path)
	for code in codes:
		if code in all_signals:
			signals_for_code = all_signals[code]
			signal_message = ''
			for signal in signals_for_code:
				sig_log_file.write(str(dt.datetime.now()) + " " + signal + "\n")
				signal_message = signal_message + "\n" + signal
			
			popupmsg(code, signal_message)

def popupmsg(code, msg):
    popup = tk.Tk()
    popup.wm_title("Scando: " + code + " activity")
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Cheers bro", command = popup.destroy)
    B1.pack()
    popup.mainloop()


#=============================================================================
# Old code that I'm not comfortable enough yet to delete
#=============================================================================

# Yahoo code: Note no date is supplied on page and data may not agree with ASX
# home_url = 'https://au.finance.yahoo.com/quote/'
# page_detail = '.AX'
# for code in codes:
# 	page = home_url + code + page_detail
# 	log_file.write(str(dt.datetime.now()) + p age
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


