import concurrent.futures
import logging
import sys
from pprint import pformat

import pandas as pd
import pyinstrument
import talib
from nsepython import nse_eq, equity_history

from constants.config import Configuration
from constants.stocks import InfoKeys, NSE
from lib.utils import Utils

logging.basicConfig(stream=sys.stdout, level=Configuration.LOG_LEVEL)


class Nifty:
    """Implements all the NSE related ops."""

    @staticmethod
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

        data = Nifty.get_historical_data(symbol)
        if not data.empty:
            # Add the calculated indicators.
            stock_info["RSI"] = Nifty.stock_rsi(symbol, data)
            stock_info["ADX"] = Nifty.stock_adx(symbol, data)
            stock_info["BB_HIGH"] = Nifty.stock_bollinger_bands(symbol, data)[0]
            stock_info["BB_AVG"] = Nifty.stock_bollinger_bands(symbol, data)[1]
            stock_info["BB_LOW"] = Nifty.stock_bollinger_bands(symbol, data)[2]
            stock_info["%K"] = Nifty.stock_stochastic(symbol, data)[0]
            stock_info["%D"] = Nifty.stock_stochastic(symbol, data)[1]
            stock_info["20-EMA"] = Nifty.stock_ema(symbol, data)

            # Deduce signal for trade.
            stock_info["Δ EMA"] = Nifty.stock_ema_delta(stock_info)
            stock_info["SIGNAL"] = Nifty.guess_trade_signal(stock_info)

        logging.debug(pformat(stock_info))
        return stock_info

    @staticmethod
    def get_historical_data(symbol: str):
        """get historical data for any stock."""
        historical_data = equity_history(
            symbol=symbol,
            series=NSE.STOCK_CODE,
            start_date=Utils.get_lookback_date(),
            end_date=Utils.get_ist_date(),
        )

        if historical_data.empty:
            logging.error(f"failed to get any data, check the symbol '{symbol}'.")
            return historical_data

        historical_data.sort_values(by=NSE.HISTCOL_SORTER, ascending=True, inplace=True)
        return historical_data

    @pyinstrument.profile()
    def show_list_info(self, stock_list: list):
        """display the stock information for each of the list element."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
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
        diff = stock_info[InfoKeys.LAST_PRICE.name] - stock_info["20-EMA"]
        diffp = (diff * 100) / stock_info["20-EMA"]
        return round(diffp, 2)

    @staticmethod
    def guess_trade_signal(stock_info):
        signal = "Weak Trend"
        adx = stock_info["ADX"] >= 25
        stoch_breach = Utils.percetage_diff(stock_info["%K"], stock_info["%D"])
        bb_high_breach = Utils.percetage_diff(
            stock_info["LAST_PRICE"], stock_info["BB_LOW"]
        )
        bb_low_breach = Utils.percetage_diff(
            stock_info["LAST_PRICE"], stock_info["BB_LOW"]
        )

        """
            1. No trend with ADX < 25.0
            2. Stochastic Oscillator intersection indicates trend reversal
            3. Proximity to BB high and low values show potential reversal
            4. Favourable RSI value indicates strong trend
        """
        if adx:
            if bb_high_breach:
                if stoch_breach:
                    if stock_info["RSI"] <= 30:
                        signal = "Strong BUY"
                    else:
                        signal = "Breakout BUY"
                else:
                    signal = "Continued Uptrend"

            if bb_high_breach:
                if stoch_breach:
                    if stock_info["RSI"] >= 70:
                        signal = "Strong SELL"
                    else:
                        signal = "Breakout SELL"
                else:
                    signal = "Continued Downtrend"

        return signal
