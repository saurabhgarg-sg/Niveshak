import logging
import sys
from pprint import pformat

import pandas as pd
import streamlit as st
import talib
from nsepython import nse_eq, equity_history

from constants.config import Configuration
from constants.stocks import InfoKeys, NSE
from lib.utils import Utils

logging.basicConfig(stream=sys.stdout, level=Configuration.LOG_LEVEL)


class Nifty:
    """Implements all the NSE related ops."""

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

        # Add the calculated indicators.
        stock_info["RSI"] = Nifty.stock_rsi(symbol)
        stock_info["ADX"] = Nifty.stock_adx(symbol)
        stock_info["BB_HIGH"] = Nifty.stock_bollinger_bands(symbol)[0]
        stock_info["BB_AVG"] = Nifty.stock_bollinger_bands(symbol)[1]
        stock_info["BB_LOW"] = Nifty.stock_bollinger_bands(symbol)[2]
        stock_info["%K"] = Nifty.stock_stochastic(symbol)[0]
        stock_info["%D"] = Nifty.stock_stochastic(symbol)[1]

        # Deduce signal for trade.
        stock_info["SIGNAL"] = Nifty.guess_trade_signal(stock_info)

        logging.debug(pformat(stock_info))
        return stock_info

    @staticmethod
    @st.cache_data
    def get_historical_data(symbol: str):
        """get historical data for any stock."""
        historical_data = equity_history(
            symbol=symbol,
            series=NSE.STOCK_CODE,
            start_date=Utils.get_lookback_date(),
            end_date=Utils.get_ist_date(),
        )
        historical_data.sort_values(by=NSE.HISTCOL_SORTER, ascending=True, inplace=True)
        return historical_data

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

    @staticmethod
    @st.cache_data
    def stock_rsi(symbol):
        data = Nifty.get_historical_data(symbol)
        rsi_data = talib.RSI(data[NSE.HISTCOL_CLOSE], int(NSE.DEFAULT_TIMEPERIOD))
        return round(float(rsi_data.iloc[-1]), 2)

    @staticmethod
    @st.cache_data
    def stock_bollinger_bands(symbol):
        data = Nifty.get_historical_data(symbol)
        bband_data = talib.BBANDS(
            data[NSE.HISTCOL_CLOSE],
            int(NSE.BBAND_TIMEPERIOD),
        )
        return [round(float(bb_data.iloc[-1]), 2) for bb_data in bband_data]

    @staticmethod
    @st.cache_data
    def stock_adx(symbol):
        data = Nifty.get_historical_data(symbol)
        adx_data = talib.ADX(
            high=data[NSE.HISTCOL_HIGH],
            low=data[NSE.HISTCOL_LOW],
            close=data[NSE.HISTCOL_CLOSE],
            timeperiod=int(NSE.DEFAULT_TIMEPERIOD),
        )
        return round(float(adx_data.iloc[-1]), 2)

    @staticmethod
    @st.cache_data
    def stock_stochastic(symbol):
        data = Nifty.get_historical_data(symbol)
        # Use the values for Stochastic Oscillator 21,5,5 for conservative medium term swing trading.
        stoch_data = talib.STOCHF(
            high=data[NSE.HISTCOL_HIGH],
            low=data[NSE.HISTCOL_LOW],
            close=data[NSE.HISTCOL_CLOSE],
            fastk_period=21,
            fastd_period=5,
        )
        return [round(float(st_data.iloc[-1]), 2) for st_data in stoch_data]

    @staticmethod
    @st.cache_data
    def guess_trade_signal(stock_info):
        signal = None
        if (
                stock_info["RSI"] >= 70
                and stock_info["ADX"] >= 25
                and Utils.percetage_diff(stock_info["LAST_PRICE"], stock_info["BB_LOW"])
                <= 1.0
        ):
            signal = "BUY"
        elif (
                stock_info["RSI"] <= 30
                and stock_info["ADX"] >= 25
                and Utils.percetage_diff(stock_info["LAST_PRICE"], stock_info["BB_HIGH"])
                >= 1.0
        ):
            signal = "SELL"
        else:
            signal = "No Trend"
        return signal
