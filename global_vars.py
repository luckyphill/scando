#global variable file

#==================================================================
# Paths to required folders
PATH = "/Users/phillipbrown/scando/"
DATA_PATH = PATH + "data/"
LOG_PATH = PATH + "logs/"
RAW_PATH = DATA_PATH + "raw_data/"
ZIP_PATH = DATA_PATH + "zip_data/"
STOCK_PATH = DATA_PATH + "stock_data/"

#==================================================================
# Paths the technical analysis folders
RSI_PATH = DATA_PATH + "rsi_data/"
BOL_PATH = DATA_PATH + "bollinger_data/"
MACD_PATH = DATA_PATH + "macd_data/"
EMA921_PATH = DATA_PATH + "ema921_data/"

#==================================================================
# Paths to files
WATCH_FILE = PATH + "watch_list.csv"
LOG_FILE = LOG_PATH + "scando.log"
SIG_LOG = LOG_PATH + "siglog.log"

#==================================================================
# URLS
URL_EOD = 'http://bigcharts.marketwatch.com/quickchart/quickchart.asp?symb=AU%3A'
URL_EOD_END = '&insttype=Stock&freq=1&show=&time=8'
URL_HISTORICAL = 'https://www.asxhistoricaldata.com/data/'

#==================================================================
# General variables
EARLIEST_DATE = 20000101
EARLIEST_YEAR = 2000
LOG_SIZE_LIMIT = 1000000
NORM_FONT 		= ("Verdana", 10)

#==================================================================
# Log file pointers
LOG = open(LOG_FILE,'a+')
LOG_SIG = open(SIG_LOG,'a+')