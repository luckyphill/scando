#!/usr/bin/python
import time
import datetime as dt
import eod
import os

# Need to specify full paths for supervisord otherwise get errors
path 			= "/Users/manda/Shares/"
log_file 		= path + 'scando.log'
checked_date 	= dt.date(2000,1,1) #initial date for when scando is first started
log_size_limit 	= 1000000 #about 10Mb

while(True):
	date 	= dt.date.today()
	day 	= dt.date.today().weekday()
	hour 	= dt.datetime.now().hour

	if (day < 5) and (hour > 16) and (checked_date < date): # if we're on a weekday after 5pm and we haven't updated already
		
		lf = open(log_file,'a')
		
		eod.scan(path, lf)
		eod.tech_update(path, lf)
		
		# run the technical eod update
		# make a popup that points out signals
		checked_date = date
		lf.write(str(dt.datetime.now()) + " Done for the day, sleeping...\n")
		lf.close()

		#clean the log file
		if (os.path.getsize(log_file) > log_size_limit):
			
			with open(log_file,'r') as lf, open("temp.log" ,"w") as out:
				#only write the last half
				lf.seek(int(log_size_limit/2))
				for line in lf:
					out.write(line)

			os.remove(log_file)
			os.rename("temp.log", log_file)

	time.sleep(3600) # check once an hour