import logging
import sys

from lib.wathclists import Watchlists

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Niveshak:

    @staticmethod
    def display_welcome_page() -> None:
        """Show the main page to start the scanners."""
        wl = Watchlists()
        list_name = wl.select_list()


Niveshak().display_welcome_page()
