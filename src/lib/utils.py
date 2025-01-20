import datetime

from constants.stocks import NSE


class Utils:
    """Collection of useful utility functions."""

    @staticmethod
    def get_ist_date(dateval=datetime.datetime.now()):
        """return IST formatted date."""
        return dateval.strftime(NSE.DATE_FORMAT)

    @staticmethod
    def get_lookback_date(delta=int(NSE.LOOKBACK_DAYS)):
        """return the start date for the historical data."""
        diff = datetime.datetime.now() - datetime.timedelta(delta)
        return Utils.get_ist_date(diff)

    @staticmethod
    def percetage_diff(price, indicator):
        """calculate the percentage difference between indicator and stock price."""
        return round((indicator - price) * 100 / price, 2)
