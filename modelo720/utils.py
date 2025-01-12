"""utils module."""
import pandas as pd
from currency_converter import CurrencyConverter
from datetime import datetime
from typing import Optional

def convert_to_eur_historical(amount: float, currency: str, date: str) -> Optional[float]:
    """
    Converts an amount from a given currency to EUR using historical exchange rates.

    Args:
        amount (float): The amount of money in the original currency.
        currency (str): The currency code (e.g., 'USD', 'GBP') of the original amount.
        date (str): The date in 'YYYY-MM-DD' format for which to fetch the exchange rate.
    
    Returns:
        float: The equivalent amount in EUR.

    Raises:
        ValueError: If the currency is not supported or the date format is incorrect.
    """
    # Initialize the currency converter
    curr_conv = CurrencyConverter()
    return curr_conv.convert(amount, currency, 'EUR', date)


def last_trading_day_of_year(year: int) -> datetime:
    """
    Returns the last trading day of a given year.

    Args:
        year (int): The year for which to find the last trading day.

    Returns:
        datetime: The last trading day of the year.
    """
    date_range = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31', freq='B')
    return date_range[-1]


def try_float(s: str) -> bool:
    """Tries to convert a string to float.

    Args:
        s (str): String

    Returns:
        bool: True if able to transform, False otherwise
    """
    if not s:
        return False
    try:
        float(s.replace(',', '.'))
        return True
    except ValueError:
        return False
    