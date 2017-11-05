#!/usr/bin/python
import time
import datetime as dt
import eod
import os
import zipfile

# Need to specify full paths for supervisord otherwise get errors
path 			= "/Users/manda/Shares/"
log_file 		= path + 'scando.log'
siglog 			= path + 'siglog.log'
watch_list 		= path + 'Watch_list.csv'
checked_date 	= dt.date(2000,1,1) #initial date for when scando is first started
dl_checked_date = checked_date # a check date for the automatic downloading of historical data
log_size_limit 	= 1000000 #about 10Mb

while(True):
	date 	= dt.date.today()
	day 	= dt.date.today().weekday()
	hour 	= dt.datetime.now().hour

	if (day < 5) and (hour > 16) and (checked_date < date): # if we're on a weekday after 5pm and we haven't updated already
		
		lf = open(log_file,'a+')
		
		codes = eod.get_codes(watch_list)
		eod.scan(codes, path, lf)
		eod.tech_update(codes, path, lf)
		
		# make a popup that points out signals
		
		lf.write(str(dt.datetime.now()) + " Done for the day, sleeping...\n")
		lf.close()

		eod.clean_log(log_file, log_size_limit)

		checked_date = date
	
	if day == 6 and hour > 16 and dl_checked_date < date:
		# See if we can update the historical data automatically
		# It has worked, but it might not forever
		eod.get_historical(lf)
		dl_checked_date = date
	
		

	time.sleep(900) # check every 15 minutes