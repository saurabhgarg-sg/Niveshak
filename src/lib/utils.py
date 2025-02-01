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
        return Utils.get_ist_date(dateval=diff)

    @staticmethod
    def percentage_diff(a, b):
        """calculate the percentage difference between b and a."""
        # sometimes for new listed entities data is not available.
        if a == 0:
            return 0.0

        return round((a - b) * 100 / a, 2)
