import concurrent.futures
import logging
import sys
from pprint import pformat

import pandas as pd
import pyinstrument
import requests
import streamlit as st
import talib
from nsepython import nse_eq, equity_history

from constants.config import Configuration
from constants.stocks import RawInfoKeys, NSE, InfoKeys
from lib.utils import Utils

logging.basicConfig(stream=sys.stdout, level=Configuration.LOG_LEVEL)


class Nifty:
    """Implements all the NSE related ops."""

    @staticmethod
    @st.cache_data
    def get_stock_info(symbol: str):
        """fetch individual stock information."""
        stock_info = {"SYMBOL": symbol}
        try:
            raw_info = nse_eq(symbol)
        except requests.exceptions.JSONDecodeError as jerr:
            logging.error(f"failed to get stock into for '{symbol}'.")
            logging.error(str(jerr))
            return stock_info

        if raw_info and raw_info.get("info"):
            logging.debug(pformat(raw_info))
        else:
            logging.error(f"failed to get info on '{symbol}'.")
            return stock_info

        logging.info(f"fetching information on '{stock_info["SYMBOL"]}'.")
        for infokey in RawInfoKeys:
            # construct the key to fetch the value.
            infoval = raw_info
            for key in infokey.value:
                infoval = infoval.get(key)
                if not infoval:
                    break
            stock_info[infokey.name] = infoval

        data = Nifty.get_historical_data(symbol)
        if len(data) != 0 and not data.empty:
            # Add the calculated indicators.
            stock_info[InfoKeys.RSI] = Nifty.stock_rsi(symbol, data)
            stock_info[InfoKeys.ADX] = Nifty.stock_adx(symbol, data)
            stock_info[InfoKeys.BB_HIGH] = Nifty.stock_bollinger_bands(symbol, data)[0]
            stock_info[InfoKeys.BB_AVG] = Nifty.stock_bollinger_bands(symbol, data)[1]
            stock_info[InfoKeys.BB_LOW] = Nifty.stock_bollinger_bands(symbol, data)[2]
            stock_info[InfoKeys.STOCH_K] = Nifty.stock_stochastic(symbol, data)[0]
            stock_info[InfoKeys.STOCH_D] = Nifty.stock_stochastic(symbol, data)[1]
            stock_info[InfoKeys.EMA_20] = Nifty.stock_ema(symbol, data)

            # Deduce signal for trade.
            stock_info["Δ EMA"] = Nifty.stock_ema_delta(stock_info)
            stock_info["SIGNAL"] = Nifty.guess_trade_signal(stock_info)

        logging.debug(pformat(stock_info))
        return stock_info

    @staticmethod
    @st.cache_data
    def get_historical_data(symbol: str):
        """get historical data for any stock."""
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

        historical_data.sort_values(by=NSE.HISTCOL_SORTER, ascending=True, inplace=True)
        return historical_data

    @pyinstrument.profile()
    def show_list_info(self, stock_list: list):
        """display the stock information for each of the list element."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(self.get_stock_info, stock_list, timeout=120)

        data = list(results)
        logging.debug(pformat(data))

        return pd.DataFrame(data)

    @staticmethod
    def stock_rsi(symbol, data):
        rsi_data = talib.RSI(data[NSE.HISTCOL_CLOSE], int(NSE.DEFAULT_TIMEPERIOD))
        return round(float(rsi_data.iloc[-1]), 2)

    @staticmethod
    def stock_bollinger_bands(symbol, data):
        bband_data = talib.BBANDS(data[NSE.HISTCOL_CLOSE], 20)
        return [round(float(bb_data.iloc[-1]), 2) for bb_data in bband_data]

    @staticmethod
    def stock_adx(symbol, data):
        adx_data = talib.ADX(
            high=data[NSE.HISTCOL_HIGH],
            low=data[NSE.HISTCOL_LOW],
            close=data[NSE.HISTCOL_CLOSE],
            timeperiod=int(NSE.DEFAULT_TIMEPERIOD),
        )
        return round(float(adx_data.iloc[-1]), 2)

    @staticmethod
    def stock_stochastic(symbol, data):
        # Use the values for Stochastic Oscillator 10,3,3 for aggressive short term swing trading.
        # Use the values for Stochastic Oscillator 21,5,5 for conservative medium term swing trading.
        stoch_data = talib.STOCHF(
            high=data[NSE.HISTCOL_HIGH],
            low=data[NSE.HISTCOL_LOW],
            close=data[NSE.HISTCOL_CLOSE],
            fastk_period=10,
            fastd_period=3,
        )
        return [round(float(st_data.iloc[-1]), 2) for st_data in stoch_data]

    @staticmethod
    def stock_ema(symbol, data):
        ema_data = talib.EMA(data[NSE.HISTCOL_CLOSE], timeperiod=20)
        return round(float(ema_data.iloc[-1]), 2)

    @staticmethod
    def stock_ema_delta(stock_info):
        diff = stock_info[InfoKeys.LAST_PRICE] - stock_info[InfoKeys.EMA_20]
        diff_percentage = (diff * 100) / stock_info[InfoKeys.EMA_20]
        return round(diff_percentage, 2)

    @staticmethod
    def find_adx_strength(adx_value):
        """return value of ADX strength."""
        if 0 < adx_value <= 25:
            logging.info("ADX: Weak Trend")
            adx_strength = 0
        elif 25 < adx_value <= 50:
            logging.info("ADX: Strong Trend")
            adx_strength = 1
        elif 50 < adx_value <= 75:
            logging.info("ADX: Very Strong Trend")
            adx_strength = 2
        elif 75 < adx_value <= 100:
            logging.info("ADX: Extremely Strong Trend")
            adx_strength = 3

        return adx_strength

    @staticmethod
    def guess_trade_signal(stock_info):
        signal_strength = 0
        signal_strength += Nifty.find_adx_strength(stock_info[InfoKeys.ADX])
        stoch_strength = Utils.percetage_diff(
            stock_info[InfoKeys.STOCH_K], stock_info[InfoKeys.STOCH_D]
        )
        bb_high_strength = Utils.percetage_diff(
            stock_info[InfoKeys.LAST_PRICE.name], stock_info[InfoKeys.BB_HIGH]
        )
        bb_avg_strength = Utils.percetage_diff(
            stock_info[InfoKeys.LAST_PRICE.name], stock_info[InfoKeys.BB_AVG]
        )
        bb_low_strength = Utils.percetage_diff(
            stock_info[InfoKeys.LAST_PRICE.name], stock_info[InfoKeys.BB_LOW]
        )
        """
            1. Determine trend strength based on ADX value
            2. Stochastic Oscillator intersection indicates trend reversal
            3. Proximity to BB high and low values show potential reversal
            4. Favourable RSI value indicates strong trend
        """
        return signal_strength
