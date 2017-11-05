#!/usr/bin/python
import time
import datetime as dt
import csv
import os
import eod
import init
import signals
import Tkinter as tk
import ttk


# Need to specify full paths for supervisord otherwise get errors
path 			= "/Users/Manda/scando/"
log_file 		= path + 'TEST_scando.log'
watch_list 		= path + 'Watch_list.csv'
lf 				= open(log_file, 'a+')
earliestDate 	= 20000101
num_days		= 10 #testing variable
NORM_FONT 		= ("Verdana", 10)
# This is purely for testing new functions/process/data handling etc.
# SHOULD NOT BE USED FOR GA TRAINING!!!!!!!!
# All testing will be done with a phantom company with code TEST
# Data for TEST comes from IFL
# New data is poached from ANZ
def popupmsg(code, msg):
    popup = tk.Tk()
    popup.wm_title("Scando: " + code + " activity")
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Cheers bro", command = popup.destroy)
    B1.pack()
    popup.mainloop()

codes = ['1AA', 'ANZ'] # all testing done with code 1AA - this puts it at the top of the folder
for code in codes:
	init.init_historical(code, earliestDate, path) # Takes the raw stock_data and turns it into technical data

#================================================================
# Make a place to "scan" from
file_scan = path + "stock_data/ANZ.csv"
with open(file_scan, 'r') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	scan_location = list(reader)
#================================================================


code = codes[0]
quote_file = path + "stock_data/" + code + ".csv"

for days in xrange(num_days):
	#============================================================
	# a faux scan to give a new line of data in stock_data
	with open(quote_file, 'a') as csvfile:
		writer = csv.writer(csvfile, delimiter=',')
		writer.writerow(scan_location[0])
		del scan_location[0]
	#============================================================

	eod.tech_update(codes, path, lf)


#================================================================
# Testing signal output
codes = eod.get_codes(watch_list)

all_signals = signals.check_for_new_signals(codes)
for code in codes:
	if code in all_signals:
		signals_for_code = all_signals[code]
		signal_message = ''
		for signal in signals_for_code:
			signal_message = signal_message + "\n" + signal
		
		popupmsg(code, signal_message)
#================================================================


# for code in codes:
# 	# If some signals have been generated, notify the user

# 	quote_file = path + "stock_data/" + code + ".csv"
# 	with open(quote_file, 'r') as f:
# 		quote_reader = csv.reader(f, delimiter=',')
# 		quote_list 	= list(quote_reader)

# 	rsi_file = path + "rsi_data/" + code + ".csv"
# 	with open(rsi_file, 'r') as f:
# 		rsi_reader = csv.reader(f, delimiter=',')
# 		rsi_list 	= list(rsi_reader)

# 	del rsi_list[0]
# 	for i in xrange(1, len(quote_list)):
# 		signal = signals.dead_cat_bounce(code, [float(quote_list[i-1][4]),float(quote_list[i][4])])
# 		# if signal:
# 		# 	popupmsg(code, signal)
# 	for i in xrange(1, len(rsi_list)):		
# 		signal = signals.rsi_breaks(code, [float(rsi_list[i-1][3]),float(rsi_list[i][3])])
# 		if signal:
# 			popupmsg(code, signal)

lf.close()

