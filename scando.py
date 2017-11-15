#!/usr/bin/python
import time
import datetime as dt
import os
import zipfile

import eod
import init

from global_vars import * #Import the fixed global variables, like file paths etc.

checked_date 	= dt.date(2000,1,1) #initial date for when scando is first started
dl_checked_date = dt.date(2000,1,1) # a check date for the automatic downloading of historical data

# Runs only once upon start up
codes = init.launch_procedure()

while(True):
	date 	= dt.date.today()
	day 	= dt.date.today().weekday()
	hour 	= dt.datetime.now().hour

	if day < 5 and hour > 16 and checked_date < date: # if we're on a weekday after 5pm and we haven't updated already

		eod.scan(codes)
		eod.tech_update(codes)
		eod.notify_of_signals(codes)
		codes = eod.check_for_watch_list_removals(codes)
		
		LOG.write(str(dt.datetime.now()) + " Done for the day, sleeping...\n")

		eod.clean_log()

		checked_date = date
	
	if day == 6 and hour > 16 and dl_checked_date < date:
		# See if we can update the historical data automatically
		# It has worked, but it might not forever
		eod.get_historical()
		codes = eod.check_for_watch_list_additions(codes)
		dl_checked_date = date
	
		

	time.sleep(900) # check every 15 minutes