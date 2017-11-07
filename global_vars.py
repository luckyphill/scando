#global variable file

PATH = "/Users/Manda/scando/"
DATA_PATH = PATH + "data/"
LOG_PATH = PATH + "logs/"
RAW_PATH = DATA_PATH + "raw_data/"
ZIP_PATH = DATA_PATH + "zip_data/"
STOCK_PATH = DATA_PATH + "stock_data/"

RSI_PATH = DATA_PATH + "rsi_data/"
BOL_PATH = DATA_PATH + "bollinger_path/"
MACD_PATH = DATA_PATH + "macd_data/"
EMA921_PATH = DATA_PATH + "ema921_data/"

WATCH_FILE = PATH + "Watch_list.csv"
LOG_FILE = LOG_PATH + "scando.log"
SIG_LOG = LOG_PATH + "siglog.log"

EARLIEST_DATE = 20000101
LOG_SIZE_LIMIT = 1000000

lf = open(LOG_FILE,'a+')
