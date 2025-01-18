import logging
import os
import sys
from pprint import pformat

import streamlit as st

from constants.datafiles import DataFiles

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Watchlists:
    """class for implement  all the watchlist related operations."""

    def __init__(self):
        self.watchlists = {}

    @staticmethod
    def read_symbols(path) -> list:
        """return the list of symbols from the watchlist."""
        content = []
        with open(path) as fh:
            content = [txt.strip() for txt in fh.readlines()]
        return content

    def get_all(self):
        """Get all the watchlists."""
        for entry in os.scandir(DataFiles.WATCHLISTS):
            if entry.is_file():
                self.watchlists[entry.name] = self.read_symbols(entry.path)
        logging.debug(pformat(self.watchlists))

    def select_list(self):
        """Show the main page to start the scanners."""
        self.get_all()
        option = st.selectbox(
            "Which list to scan?",
            sorted(self.watchlists.keys()),
            index=None,
            placeholder="select a list",
        )
        st.write("displaying watchlist: ", option)
        return option
