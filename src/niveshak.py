import logging
import sys

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
            self.show_watchlist_info()

    def show_watchlist_info(self):
        """display the information about all the symbols in the list."""
        nse = Nifty()
        st.write(nse.show_list_info(stock_list=self.list_symbols))
        st.write(nse.get_historical_data("SBIN"))

    def display_welcome_page(self) -> None:
        """Show the main page to start the scanners."""
        self.select_list()
        logging.debug(f"fetching information on the stocks for '{self.list_name}'.")


Niveshak().display_welcome_page()
