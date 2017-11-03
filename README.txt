For the share price data analysis we need:
	Stuff for scraping the data:
		Beautifulsoup: easy_install beautifulsoup4
		A parser for Beautifulsoup: easy_install lxml
		Requests (for doing url stuff): easy_install requests
	Stuff for daemonising the processes:
		Supervisord: easy_install supervisor
		A modified config file for supervisord
		A plist file to run supervisord on startup
	Stuff for the pop up notificaions:
		TBD

This bunch of scripts grabs EoD data for all the company codes listed in Watch_list.txt
It cannot get historical data. If more data is needed, visit https://www.asxhistoricaldata.com/ for free data
which must be manually downloaded, unzipped and stored in the folder raw_data.
If you have new raw data, you must run clean_raw_data.py to put it in a form for each individual company - this may take a few minutes

If your historical data is up to date then the background process can be left to run autonomously
At around 5pm it will look up EoD data from http://bigcharts.marketwatch.com for all codes in Watch_list.txt
If the website changes at all, then auto update will fail

With the new data, it will run a technical analysis on all companies in Watch_list.txt and popup a notification if any buy or sell signals are generated





Daemonising on MacOSX with supervisord
http://supervisord.org/index.html
https://stackoverflow.com/questions/9522324/running-python-in-background-on-os-x
https://gist.github.com/fadhlirahim/78fefdfdf4b96d9ea9b8
https://nicksergeant.com/running-supervisor-on-os-x/

download the package: sudo easy_install supervisor

To make supervisor un on start up, you need to make a plist file in:
~/Library/LaunchAgents/com.agendaless.supervisord.plist

An example is given below ([1]) from the above linked github account:
This example forces supervisord to look for it's conf file in 
/usr/local/share/supervisor/supervisord.conf
Other options are
/usr/local/share/etc/supervisord.conf
/usr/local/share/supervisord.conf

Next you need to add the file you want to run into the supervisord config file.
In the 





[1] - File to make supervisord run on startup
<!-- /Library/LaunchDaemons/com.agendaless.supervisord.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    <key>Label</key>
    <string>com.agendaless.supervisord</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/supervisord</string>
        <string>-n</string> 
        <string>-c</string>
        <string>/usr/local/share/supervisor/supervisord.conf</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>




