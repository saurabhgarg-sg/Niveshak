from pprint import pprint

import pandas
from nsepython import *

# nsepython demo
pandas.set_option("display.max_rows", None)
pandas.set_option("display.max_columns", None)
# pprint(indices)
# pprint(nse_eq("ABSLPSE"))
try:
    test = nse_eq("RAYMOND")
    pprint(test)
except requests.exceptions.JSONDecodeError as e:
    print("failed to fetch data for stock symbol")
# pprint(nse_get_top_gainers())
# test = equity_history("SBIN", "EQ", "01-06-2024", "18-01-2025")
# test = equity_history("ABSLPSE", "EQ", "01-06-2024", "18-01-2025")
# pprint(test)
# pprint(test.loc[[1]])
