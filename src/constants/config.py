import logging


class Configuration:
    """stores the app wide configuration parameters."""

    LOG_LEVEL = logging.INFO
    LIVE_DATA_TIMEOUT = 120
    CONCURRENCY = 10
