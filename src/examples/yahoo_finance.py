from pprint import pprint
import yfinance as yf

dat = yf.Ticker("SAIL.NS")
pprint(dat.fast_info)
# pprint(dat.info)
# pprint(dat.calendar)
# pprint(dat.analyst_price_targets)
# pprint(dat.quarterly_income_stmt)
# pprint(dat.history(period="6mo"))
