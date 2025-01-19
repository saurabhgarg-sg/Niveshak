import logging
import sys
from pprint import pformat

import pandas as pd
import streamlit as st
from nsepython import nse_eq

from constants.config import Configuration
from constants.stocks import InfoKeys

logging.basicConfig(stream=sys.stdout, level=Configuration.LOG_LEVEL)


class Nifty:
    """Implements all the NSE related ops."""

    def __init__(self):
        pass

    @staticmethod
    @st.cache_data
    def get_stock_info(symbol: str):
        """fetch individual stock information."""
        raw_info = nse_eq(symbol)
        assert raw_info, f"failed to get info on '{symbol}'."
        logging.debug(pformat(raw_info))

        stock_info = {"SYMBOL": symbol}
        for infokey in InfoKeys:
            # construct the key to fetch the value.
            infoval = raw_info
            for key in infokey.value:
                infoval = infoval[key]
            stock_info[infokey.name] = infoval
        logging.debug(pformat(stock_info))
        return stock_info

    def show_list_info(self, stock_list: list):
        """display the stock information for each of the list element."""
        # Configure progress bar to display.
        progress = 0
        bar = st.progress(progress)
        counter = 1 / len(stock_list)

        # Fetch the quotes for each stock in the watchlist.
        data = []
        for stock in stock_list:
            progress += counter
            bar.progress(progress)
            data.append(self.get_stock_info(stock))
        logging.debug(pformat(data))

        return pd.DataFrame(data)
