from enum import Enum, StrEnum


class InfoKeys(Enum):
    """List of all the keys of interest from Nifty stock data.`"""

    """Informational"""
    BASIC_INDSUTRY = ["industryInfo", "basicIndustry"]
    INDSUTRY = ["industryInfo", "industry"]
    SECTOR = ["industryInfo", "sector"]
    COMPANY_NAME = ["info", "companyName"]

    """Price information"""
    LAST_PRICE = ["priceInfo", "lastPrice"]
    LAST_CLOSE = ["priceInfo", "previousClose"]
    INTRADAY_HIGH = ["priceInfo", "intraDayHighLow", "max"]
    INTRADAY_LOW = ["priceInfo", "intraDayHighLow", "min"]
    YEAR_HIGH = ["priceInfo", "weekHighLow", "max"]
    YEAR_LOW = ["priceInfo", "weekHighLow", "min"]
    UPPER_CKT = ["priceInfo", "upperCP"]
    LOWER_CKT = ["priceInfo", "lowerCP"]


class NSE(StrEnum):
    """NSE stock related constants."""

    STOCK_CODE = "EQ"
    DATE_FORMAT = "%d-%m-%Y"
    LOOKBACK_DAYS = "180"

    # Historical data columns.
    HISTCOL_CLOSE = "CH_CLOSING_PRICE"
    HISTCOL_HIGH = "CH_TRADE_HIGH_PRICE"
    HISTCOL_LOW = "CH_TRADE_LOW_PRICE"
    HISTCOL_SORTER = "CH_TIMESTAMP"

    # Indicator settings.
    DEFAULT_TIMEPERIOD = "14"
    BBAND_TIMEPERIOD = "20"
    BBAND_DEVIATION = "2"
