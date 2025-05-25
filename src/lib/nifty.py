import logging
import pprint
import sys
from pprint import pformat
from urllib.parse import quote

import requests
import talib

from constants.config import Configuration, LiveDataLibrary
from constants.stocks import RawInfoKeys, NSE, InfoKeys, RawInfoKeysYF
from lib.nifty_live import NiftyLive
from lib.utils import Utils

logging.basicConfig(stream=sys.stdout, level=Configuration.LOG_LEVEL)


class Nifty:
    """Implements all the NSE related ops."""

    def __init__(self):
        self.stock_info = None
        self.stock_history = None
        self.safe_symbol = None

        self.stock_history_close = NSE.YF_HISTCOL_CLOSE
        self.stock_history_high = NSE.YF_HISTCOL_HIGH
        self.stock_history_low = NSE.YF_HISTCOL_LOW

        if Configuration.LIVE_DATA_LIB == LiveDataLibrary.NSEPYTHON:
            self.stock_history_close = NSE.HISTCOL_CLOSE
            self.stock_history_high = NSE.HISTCOL_HIGH
            self.stock_history_low = NSE.HISTCOL_LOW

    def get_stock_info(self, symbol: str):
        """fetch individual stock information."""
        self.stock_info = {InfoKeys.SYMBOL: symbol}
        self.safe_symbol = quote(symbol, safe="")
        raw_info = None
        try:
            raw_info = NiftyLive.get_stock_quotes(self.safe_symbol)
        except requests.exceptions.JSONDecodeError as json_err:
            logging.error(f"failed to get stock into for '{symbol}'.")
            logging.error(str(json_err))

        if raw_info and (
            Configuration.LIVE_DATA_LIB == LiveDataLibrary.YFINANCE
            or (
                Configuration.LIVE_DATA_LIB == LiveDataLibrary.NSEPYTHON
                and raw_info.get("info")
            )
        ):
            logging.debug(pformat(raw_info))
        else:
            logging.error(f"failed to get info on '{symbol}'.")
            return None

        logging.info(f"fetching information on '{self.stock_info[InfoKeys.SYMBOL]}'.")
        if Configuration.LIVE_DATA_LIB == LiveDataLibrary.YFINANCE:
            for infokey in RawInfoKeysYF:
                self.stock_info[infokey.name] = raw_info.get(infokey, 0)

            # For ETFs YF does not give currentPrice, but populates regularMarketPrice
            # So, manually populate that column in case of ETFs
            if (
                self.stock_info[InfoKeys.LAST_PRICE] == 0
                and RawInfoKeysYF.ETF_LAST_PRICE in raw_info
            ):
                self.stock_info[InfoKeys.LAST_PRICE] = raw_info[
                    RawInfoKeysYF.ETF_LAST_PRICE
                ]
            self.stock_info.pop(RawInfoKeysYF.ETF_LAST_PRICE.name)
        else:
            for infokey in RawInfoKeys:
                # construct the key to fetch the value.
                infoval = raw_info
                for key in infokey.value:
                    infoval = infoval.get(key)
                    if not infoval:
                        break
                self.stock_info[infokey.name] = infoval
        del raw_info
        logging.debug("stock info")
        logging.debug(pprint.pformat(self.stock_info))

        self.stock_history = NiftyLive.get_historical_data(self.safe_symbol)
        logging.debug(pprint.pformat(self.stock_history))
        if len(self.stock_history) != 0 and not self.stock_history.empty:
            # Add the calculated indicators.
            self.stock_info[InfoKeys.RSI] = self.stock_rsi()
            self.stock_info[InfoKeys.ADX] = self.stock_adx()
            self.stock_info[InfoKeys.BB_HIGH] = self.stock_bollinger_bands()[0]
            self.stock_info[InfoKeys.BB_AVG] = self.stock_bollinger_bands()[1]
            self.stock_info[InfoKeys.BB_LOW] = self.stock_bollinger_bands()[2]
            self.stock_info[InfoKeys.STOCH_K] = self.stock_stochastic()[0]
            self.stock_info[InfoKeys.STOCH_D] = self.stock_stochastic()[1]
            self.stock_info[InfoKeys.EMA_20] = self.stock_ema()

            # Deduce signal for trade.
            self.stock_info[InfoKeys.EMA_DELTA] = self.stock_ema_delta()
            self.guess_trade_signal()

        logging.debug(pformat(self.stock_info))
        return self.stock_info

    def stock_rsi(self):
        rsi_data = talib.RSI(
            self.stock_history[self.stock_history_close], int(NSE.DEFAULT_TIMEPERIOD)
        )
        return round(float(rsi_data.iloc[-1]), 2)

    def stock_bollinger_bands(self):
        bband_data = talib.BBANDS(self.stock_history[self.stock_history_close], 20)
        return [round(float(bb_data.iloc[-1]), 2) for bb_data in bband_data]

    def stock_adx(self):

        adx_data = talib.ADX(
            high=self.stock_history[self.stock_history_high],
            low=self.stock_history[self.stock_history_low],
            close=self.stock_history[self.stock_history_close],
            timeperiod=int(NSE.DEFAULT_TIMEPERIOD),
        )
        return round(float(adx_data.iloc[-1]), 2)

    def stock_stochastic(self):
        # Use the values for Stochastic Oscillator 10,3,3 for aggressive short term swing trading.
        # Use the values for Stochastic Oscillator 21,5,5 for conservative medium term swing trading.
        stoch_data = talib.STOCH(
            high=self.stock_history[self.stock_history_high],
            low=self.stock_history[self.stock_history_low],
            close=self.stock_history[self.stock_history_close],
            fastk_period=10,
        )
        return [round(float(st_data.iloc[-1]), 2) for st_data in stoch_data]

    def stock_ema(self):
        ema_data = talib.EMA(
            self.stock_history[self.stock_history_close], timeperiod=20
        )
        return round(float(ema_data.iloc[-1]), 2)

    def stock_ema_delta(self):
        return Utils.percentage_diff(
            self.stock_info[InfoKeys.LAST_PRICE], self.stock_info[InfoKeys.EMA_20]
        )

    def find_adx_trend(self):
        """return value of ADX strength."""
        adx_strength = 0
        msg = ""
        if 0 < self.stock_info[InfoKeys.ADX] <= 25:
            msg = "Weak"
        elif 25 < self.stock_info[InfoKeys.ADX] <= 50:
            msg = "Strong"
            adx_strength = 1
        elif 50 < self.stock_info[InfoKeys.ADX] <= 75:
            msg = "Very Strong"
            adx_strength = 2
        elif self.stock_info[InfoKeys.ADX] > 75:
            msg = "Extremely Strong"
            adx_strength = 3

        self.stock_info[InfoKeys.SIGNAL] = msg
        return adx_strength

    def find_stoch_trend(self):
        """return value of Stochastic strength."""
        msg = ""
        stoch_diff = Utils.percentage_diff(
            self.stock_info[InfoKeys.STOCH_D], self.stock_info[InfoKeys.STOCH_K]
        )
        self.stock_info[InfoKeys.STOCH_DELTA] = f"{stoch_diff}%"

        if -7.5 <= stoch_diff <= 7.5:
            msg = "Breakout"
        elif (
            self.stock_info[InfoKeys.STOCH_K] > 80
            or self.stock_info[InfoKeys.STOCH_K] < 20
        ):
            msg = "Reversal"
        elif 20 < self.stock_info[InfoKeys.STOCH_K] < 80:
            if stoch_diff < -7.5:
                msg = "Uptrend"
            else:
                msg = "Downtrend"

        if self.stock_info[InfoKeys.STOCH_K] > self.stock_info[InfoKeys.STOCH_D]:
            msg += " Rise"
        else:
            msg += " Fall"
        self.stock_info[InfoKeys.SIGNAL] += f" {msg}"

    def find_bb_trend(self):
        """return Bollinger band signal"""
        msg = ""

        if self.stock_info[InfoKeys.LAST_PRICE] > self.stock_info[InfoKeys.BB_HIGH]:
            msg = "Sell."
        elif self.stock_info[InfoKeys.LAST_PRICE] < self.stock_info[InfoKeys.BB_LOW]:
            msg = "Buy."
        else:
            msg = "."
        self.stock_info[InfoKeys.SIGNAL] += f" {msg}"

    def guess_trade_signal(self):
        self.find_adx_trend()
        self.find_stoch_trend()
        self.find_bb_trend()
