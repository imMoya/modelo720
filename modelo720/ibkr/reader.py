"""ibkr reader for modelo720."""

from pathlib import Path

import polars as pl

from modelo720.utils import (
    convert_to_eur_historical,
    last_trading_day_of_year,
    try_float,
)

from .references import COLUMNS_DICT, DESIRED_SCHEMA


class IbkrReader:
    """Reads the IBKR portfolio CSV file."""

    def __init__(self, file_path: str | Path, year: int):
        """Initializes class to read CSV.

        Args:
            file_path (Union[str, Path]): file path of the portfolio
        """
        self.file_path = Path(file_path)
        self.year = year

    @property
    def data(self):
        """Performs data transformations."""
        self._data = self.read_dataset()
        self._data = self._data.rename(COLUMNS_DICT).select(list(COLUMNS_DICT.values()))
        last_trading_day = last_trading_day_of_year(self.year)
        self._data = self._data.with_columns(
            pl.struct(["local_value", "local_curr"])
            .map_elements(
                lambda x: convert_to_eur_historical(x["local_value"], x["local_curr"], last_trading_day),
                return_dtype=float,
            )
            .alias("eur_value")
        )
        self._data = self._data.cast(DESIRED_SCHEMA)
        return self._data

    def read_dataset(self):
        """Reads the file."""
        data = pl.read_csv(self.file_path)
        return data

    @staticmethod
    def convert_num_columns(df: pl.DataFrame) -> pl.DataFrame:
        """Convert columns to numeric.

        Args:
            df (pl.DataFrame): polars dataframe

        Returns:
            pl.DataFrame: reformatted dataframe with numeric columns
        """
        for col in df.columns:
            if df[col].dtype in [pl.Float64, pl.Int64]:
                continue
            else:
                try:
                    sample = df[col].drop_nulls().head(10)
                    if sample.is_empty():
                        continue

                    if sample.map_elements(try_float, return_dtype=pl.Float64).sum() > 0:
                        df = df.with_columns([pl.col(col).str.replace(",", ".").cast(pl.Float64).alias(col)])
                except Exception:
                    continue

        return df
