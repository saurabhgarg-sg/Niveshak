from enum import Enum, StrEnum


class RawInfoKeys(Enum):
    """List of all the keys of interest from Nifty stock data."""

    """Price information"""
    LAST_PRICE = ["priceInfo", "lastPrice"]
    LAST_CLOSE = ["priceInfo", "previousClose"]
    INTRADAY_HIGH = ["priceInfo", "intraDayHighLow", "max"]
    INTRADAY_LOW = ["priceInfo", "intraDayHighLow", "min"]
    YEAR_HIGH = ["priceInfo", "weekHighLow", "max"]
    YEAR_LOW = ["priceInfo", "weekHighLow", "min"]
    UPPER_CKT = ["priceInfo", "upperCP"]
    LOWER_CKT = ["priceInfo", "lowerCP"]


class RawInfoKeysYF(StrEnum):
    """List of all the keys of interest from Yahoo finance stock data."""

    LAST_CLOSE = "previousClose"
    INTRADAY_HIGH = "dayHigh"
    INTRADAY_LOW = "dayLow"
    YEAR_HIGH = "fiftyTwoWeekHigh"
    YEAR_LOW = "fiftyTwoWeekLow"


class InfoKeys(StrEnum):
    """Keys for parsed information."""

    ADX = "ADX"
    BB_HIGH = "BB_HIGH"
    BB_AVG = "BB_MID"
    BB_LOW = "BB_LOW"
    EMA_20 = "20-EMA"
    EMA_DELTA = "Δ EMA"
    LAST_PRICE = "LAST_PRICE"
    RSI = "RSI"
    SIGNAL = "SIGNAL"
    STOCH_K = "%K"
    STOCH_D = "%D"
    STOCH_DELTA = "Δ STOCH"
    SYMBOL = "SYMBOL"


class NSE(StrEnum):
    """NSE stock related constants."""

    STOCK_CODE = "EQ"
    DATE_FORMAT = "%d-%m-%Y"
    LOOKBACK_DAYS = "180"
    YF_LOOKBACK_PERIOD = "6mo"

    # Historical data columns.
    HISTCOL_CLOSE = "CH_CLOSING_PRICE"
    HISTCOL_HIGH = "CH_TRADE_HIGH_PRICE"
    HISTCOL_LOW = "CH_TRADE_LOW_PRICE"
    HISTCOL_SORTER = "CH_TIMESTAMP"

    YF_HISTCOL_SORTER = "Date"

    # Indicator settings.
    DEFAULT_TIMEPERIOD = "14"
