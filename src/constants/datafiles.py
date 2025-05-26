from enum import StrEnum


class DataFiles(StrEnum):
    # files containing list of symbols to track.
    WATCHLISTS = "src/data/watchlists"
    NSE_WATCHLISTS = "src/data/nse-watchlists"
