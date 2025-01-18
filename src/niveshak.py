import logging
import os
import sys
from pprint import pformat

import streamlit as st

from constants.datafiles import DataFiles

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Niveshak:
    @staticmethod
    def get_watchlists() -> dict:
        """Get all the watchlists.
        :rtype: dict
        """
        watchlists = {}
        for entry in os.scandir(DataFiles.WATCHLISTS):
            if entry.is_file():
                watchlists[entry.name] = entry.path
        logging.debug(pformat(watchlists))
        return watchlists

    def display_welcome_page(self) -> None:
        """Show the main page to start the scanners."""
        watchlists = self.get_watchlists()
        option = st.selectbox(
            "Which list to scan?",
            sorted(watchlists.keys()),
            index=None,
            placeholder="select a list",
        )


Niveshak().display_welcome_page()
