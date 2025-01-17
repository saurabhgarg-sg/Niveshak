import os

import streamlit as st

from constants.datafiles import DataFiles


class Niveshak:
    def get_watchlists(self) -> dict:
        """Get all the watchlists."""
        watchlists = {}
        for entry in os.scandir(DataFiles.WATCHLISTS):
            if entry.is_file():
                watchlists[entry.name] = entry.path
        return watchlists

    def display_welcome_page(self):
        """Show the main page to start the scanners."""
        watchlists = self.get_watchlists()
        option = st.selectbox(
            "Which list to scan?",
            sorted(watchlists.keys()),
            index=None,
            placeholder="select a list",
        )


Niveshak().display_welcome_page()
