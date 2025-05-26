from pprint import pprint

import pandas
import yfinance as yf

# dat = yf.Ticker("NIFTYBEES.NS")
dat = yf.Ticker("^NSEI")
# pprint(dat.fast_info)
pprint(dat.info)
# pprint(dat.calendar)
# pprint(dat.analyst_price_targets)
# pprint(dat.quarterly_income_stmt)
pandas.set_option("display.max_rows", None)
pandas.set_option("display.max_columns", None)
# historical_data = dat.history(period="6mo")
# historical_data = dat.history(period="1d")
# pprint(historical_data)
