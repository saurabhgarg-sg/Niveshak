import concurrent.futures
import logging
import sys
from pprint import pformat

import pandas as pd
import pyinstrument
import streamlit as st

from constants.config import Configuration
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

    @pyinstrument.profile()
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
        logging.debug(pformat(data))
        return pd.DataFrame(data)

    def display_welcome_page(self) -> None:
        """Show the main page to start the scanners."""
        self.select_list()
        logging.debug(f"fetching information on the stocks for '{self.list_name}'.")


if __name__ == "__main__":
    Niveshak().display_welcome_page()
