from pprint import pprint

from nsepython import *

# # nsepython demo
# pandas.set_option("display.max_rows", None)
# pandas.set_option("display.max_columns", None)
# pprint(indices)
# pprint(nse_eq("ABSLPSE"))
pprint(nse_eq("SBIN"))
# pprint(nse_get_top_gainers())
# test = equity_history("SBIN", "EQ", "01-06-2024", "18-01-2025")
test = equity_history("SBIN", "EQ", "17-01-2025", "17-01-2025")
pprint(test)
# pprint(test.loc[[1]])
