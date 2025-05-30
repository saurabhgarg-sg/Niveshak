from pprint import pprint

import curl_cffi
import pandas
import yfinance as yf

# dat = yf.Ticker("NIFTYBEES.NS")
dat = yf.Ticker("SBIN1.NS")
try:
    isin = dat.isin
except curl_cffi.requests.exceptions.HTTPError:
    print("invalid stock symbol")
# pprint(dat.fast_info)
dat = yf.Ticker("SBIN.NS")
pprint(dat.info)
# pprint(dat.calendar)
# pprint(dat.analyst_price_targets)
# pprint(dat.quarterly_income_stmt)
pandas.set_option("display.max_rows", None)
pandas.set_option("display.max_columns", None)
# historical_data = dat.history(period="6mo")
# historical_data = dat.history(period="1d")
# pprint(historical_data)
