"""class to implement live data fetching.
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
import time

logging.basicConfig(stream=sys.stdout, level=Configuration.LOG_LEVEL)


class NiftyLive:

    @staticmethod
    def get_stock_quotes(symbol: str):
        """fetch individual stock information."""
        attempts = 3
        stock_quotes = {}
        while attempts > 0:
            try:
                stock_quotes = nse_eq(quote(symbol, safe=""))
                break
            except requests.exceptions.JSONDecodeError as e:
                print(f"failed to fetch data for stock symbol {symbol}")
                attempts -= 1
                time.sleep(3)

        return stock_quotes

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
