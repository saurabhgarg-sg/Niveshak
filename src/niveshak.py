import concurrent.futures
import logging
import sys

import pandas as pd
import pyinstrument
import streamlit as st

from constants.config import Configuration
from constants.stocks import InfoKeys, RawInfoKeys
from lib.nifty import Nifty
from lib.wathclists import Watchlists

logging.basicConfig(stream=sys.stdout, level=Configuration.LOG_LEVEL)


class Niveshak:

    def __init__(self):
        self.list_name = None
        self.list_symbols = None

    def select_list(self):
        """Show the main page to start the scanners."""
        wl = Watchlists()
        wl.get_all()
        self.list_name = st.selectbox(
            "Which list to scan?",
            sorted(wl.watchlists.keys()),
            index=None,
            placeholder="select a list",
        )
        st.write("displaying watchlist: ", self.list_name)
        if self.list_name:
            self.list_symbols = wl.watchlists[self.list_name]
            st.write(self.show_list_info())

    @pyinstrument.profile(use_timing_thread=True)
    def show_list_info(self):
        """display the stock information for each of the list element."""
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=Configuration.CONCURRENCY
        ) as executor:
            results = executor.map(
                Nifty().get_stock_info,
                self.list_symbols,
                timeout=Configuration.LIVE_DATA_TIMEOUT,
            )

        data = list(results)
        return self.arrange_display_columns(pd.DataFrame(data))

    @staticmethod
    def arrange_display_columns(df):
        """re-arrange the column display order."""
        new_order = [
            InfoKeys.SYMBOL,
            InfoKeys.SIGNAL,
            InfoKeys.EMA_DELTA,
            InfoKeys.RSI,
            InfoKeys.ADX,
            InfoKeys.EMA_20,
            InfoKeys.STOCH_DELTA,
            InfoKeys.STOCH_K,
            InfoKeys.STOCH_D,
            InfoKeys.BB_HIGH,
            InfoKeys.BB_AVG,
            InfoKeys.BB_LOW,
            InfoKeys.LAST_PRICE,
            RawInfoKeys.INTRADAY_HIGH.name,
            RawInfoKeys.INTRADAY_LOW.name,
            RawInfoKeys.LAST_CLOSE.name,
            RawInfoKeys.YEAR_HIGH.name,
            RawInfoKeys.YEAR_LOW.name,
            RawInfoKeys.UPPER_CKT.name,
            RawInfoKeys.LOWER_CKT.name,
        ]

        try:
            arranged_df = df[new_order]
        except KeyError as kerr:
            logging.error(f"failed to arrange the columns: {str(kerr)}")
            return df
        return arranged_df

    def display_welcome_page(self) -> None:
        """Show the main page to start the scanners."""
        self.select_list()
        logging.debug(f"fetching information on the stocks for '{self.list_name}'.")


if __name__ == "__main__":
    Niveshak().display_welcome_page()
