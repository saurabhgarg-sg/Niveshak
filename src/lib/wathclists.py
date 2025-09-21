import logging
import os
import sys
from pprint import pformat

from constants.config import Configuration
from constants.datafiles import DataFiles

logging.basicConfig(stream=sys.stdout, level=Configuration.LOG_LEVEL)


class Watchlists:
    """class for implement  all the watchlist related operations."""

    def __init__(self):
        self.watchlists = {}
        self.exclude_list = ".DS_Store"

    @staticmethod
    def read_symbols(path) -> list:
        """return the list of symbols from the watchlist."""
        symbols = []
        with open(path) as fh:
            symbols = [symbol.strip() for symbol in fh.readlines() if len(symbol) != 0]
        return symbols

    def get_all_lists(self):
        """Get all the nse-watchlists."""
        for entry in os.scandir(DataFiles.WATCHLISTS):
            if entry.is_file() and entry.name not in self.exclude_list:
                logging.info(f"reading {entry.name}")
                self.watchlists[entry.name] = self.read_symbols(entry.path)
        logging.debug(pformat(self.watchlists))
