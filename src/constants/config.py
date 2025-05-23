import logging


class Configuration:
    """stores the app wide configuration parameters."""

    LOG_LEVEL = logging.DEBUG
    LIVE_DATA_TIMEOUT = 120
    CONCURRENCY = 10
    LIVE_DATA_LIB = "yfinance"


class LiveDataLibrary:
    NSEPYTHON = "nsepython"
    YFINANCE = "yfinance"
