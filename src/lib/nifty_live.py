"""class to implement live data fetching.
This separate class is a collection of static methods to allow caching.
"""

import logging
import pprint
import sys

import curl_cffi
import requests
import streamlit as st
from nsepython import nse_eq, equity_history

from constants.config import Configuration, LiveDataLibrary
from constants.stocks import NSE
from lib.utils import Utils
from urllib.parse import quote
import time
import yfinance as yf

logging.basicConfig(stream=sys.stdout, level=Configuration.LOG_LEVEL)


class NiftyLive:

    @staticmethod
    def get_stock_quotes(symbol: str):
        """fetch individual stock information."""
        attempts = 3
        stock_quotes = {}
        while attempts > 0:
            try:
                stock_quotes = None
                if Configuration.LIVE_DATA_LIB == LiveDataLibrary.YFINANCE:
                    stock_quotes = yf.Ticker(symbol).info
                else:
                    stock_quotes = nse_eq(symbol)
                break
            except requests.exceptions.JSONDecodeError as e:
                print(f"failed to fetch data for stock symbol {symbol}")
                attempts -= 1
                time.sleep(3)
        logging.debug(symbol)
        logging.debug(pprint.pformat(stock_quotes))
        return stock_quotes

    @staticmethod
    def get_historical_data(symbol: str):
        """get historical data for any stock."""
        historical_data = None
        if Configuration.LIVE_DATA_LIB == LiveDataLibrary.YFINANCE:
            yf_ticker = yf.Ticker(symbol)
            historical_data = yf_ticker.history(period=NSE.YF_LOOKBACK_PERIOD)
        else:
            try:
                historical_data = equity_history(
                    symbol=symbol,
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

        sorter_col = NSE.YF_HISTCOL_SORTER
        if Configuration.LIVE_DATA_LIB == LiveDataLibrary.NSEPYTHON:
            sorter_col = NSE.HISTCOL_SORTER
        historical_data.sort_values(by=sorter_col, ascending=True, inplace=True)
        return historical_data
