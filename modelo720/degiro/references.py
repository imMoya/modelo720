"""degiro references."""

import polars as pl

COLUMNS_DICT = {
    "Producto": "product",
    "Symbol/ISIN": "isin",
    "Cantidad": "amount",
    "Precio de": "price",
    "Valor local": "local_value",
    "Valor en EUR": "eur_value",
}
DESIRED_SCHEMA = {
    "product": pl.Utf8,
    "isin": pl.Utf8,
    "amount": pl.Float64,
    "local_value": pl.Float64,
    "local_curr": pl.Utf8,
    "eur_value": pl.Float64,
}
