from pprint import pprint

from nsepython import *

# # nsepython demo
# pandas.set_option('display.max_rows', None)
# pandas.set_option('display.max_columns', None)
#
#
# pprint(indices)
pprint(nse_eq("JUSTDIAL"))
# pprint(nse_eq("SBIETFIT"))
pprint(nse_get_top_gainers())
test = equity_history("SBIETFIT", "EQ", "01-01-2025", "10-01-2025")
pprint(test.loc[[1]])

### yfinance returned errors for most of the calls made
# import yfinance as yf
# dat = yf.Ticker('RELIANCE.NS')
