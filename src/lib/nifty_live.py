""" class to implement live data fetching.
    This separate class is a collection of static methods to allow caching.
"""

import logging
import sys

import requests
import streamlit as st
from nsepython import nse_eq, equity_history

from constants.config import Configuration
from constants.stocks import NSE
from lib.utils import Utils
from urllib.parse import quote

logging.basicConfig(stream=sys.stdout, level=Configuration.LOG_LEVEL)


class NiftyLive:

    @staticmethod
    @st.cache_data
    def get_stock_quotes(symbol: str):
        """fetch individual stock information."""
        return nse_eq(quote(symbol, safe=""))

    @staticmethod
    @st.cache_data
    def get_historical_data(symbol: str):
        """get historical data for any stock."""
        try:
            historical_data = equity_history(
                symbol=quote(symbol, safe=""),
                series=NSE.STOCK_CODE,
                start_date=Utils.get_lookback_date(),
                end_date=Utils.get_ist_date(),
            )
        except requests.exceptions.JSONDecodeError as jerr:
            logging.error(f"failed to get any response for '{symbol}'.")
            logging.error(str(jerr))
            return {}

        if historical_data.empty:
            logging.error(f"failed to get any data, check the symbol '{symbol}'.")
            return {}

        historical_data.sort_values(by=NSE.HISTCOL_SORTER, ascending=True, inplace=True)
        return historical_data
