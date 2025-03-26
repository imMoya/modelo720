"""ibkr references."""

import polars as pl

COLUMNS_DICT = {
    "Description": "product",
    "ISIN": "isin",
    "Quantity": "amount",
    "PositionValue": "local_value",
    "CurrencyPrimary": "local_curr",
}
DESIRED_SCHEMA = {
    "product": pl.Utf8,
    "isin": pl.Utf8,
    "amount": pl.Float64,
    "local_value": pl.Float64,
    "local_curr": pl.Utf8,
    "eur_value": pl.Float64,
}
