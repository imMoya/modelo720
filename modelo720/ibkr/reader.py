"""ibkr reader for modelo720."""

import csv
from functools import cached_property
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

    @cached_property
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


class IbkrActivity:
    """Reads the IBKR activity CSV file."""

    def __init__(self, file_path: str | Path, year: int):
        """Initializes class to read CSV.

        Args:
            file_path (Union[str, Path]): file path of the activity file
        """
        self.file_path = Path(file_path)
        self.year = year

    @cached_property
    def raw_lines(self):
        with open(self.file_path) as f:
            raw_lines = f.readlines()
        return raw_lines

    @cached_property
    def instruments(self):
        return (
            self.get_data_with_id(self.raw_lines, "Financial Instrument Information")
            .filter(pl.col("Asset Category") == "Stocks")
            .select([pl.col("Security ID").alias("isin"), pl.col("Symbol")])
        )

    @cached_property
    def trades(self):
        return self.get_data_with_id(self.raw_lines, "Trades").filter(pl.col("Asset Category") == "Stocks")

    @cached_property
    def last_sale_data(self):
        return (
            self.trades
            # Filter out SubTotal rows
            .filter(~pl.col("Header").cast(str).str.contains("SubTotal"))
            # Replace commas with dots for proper float parsing
            .with_columns(
                [
                    pl.col("Quantity").str.replace(",", "").map_elements(lambda x: x if x else None).cast(pl.Float64),
                    pl.col("Date/Time")
                    .str.replace(",", "")
                    .map_elements(lambda x: x if x else None)
                    .str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S", strict=False),
                ]
            )
            # # Only keep sales (Quantity < 0)
            .filter(pl.col("Quantity") < 0)
            # # For each symbol, get the last sale date
            .sort("Date/Time", descending=True)
            .group_by("Symbol")
            .agg(pl.col("Date/Time").first().alias("Last_Sale_Date"))
        )

    @cached_property
    def exit_data(self):
        df = self.trades.filter(pl.col("Header").cast(str).str.contains("SubTotal")).filter(
            pl.col("Quantity").cast(pl.Float64) < 0
        )
        df = df.join(self.last_sale_data, on="Symbol", how="left")
        df = df.join(self.instruments, on="Symbol", how="left")
        df = df.with_columns(
            [
                pl.struct(["Proceeds", "Currency", "Last_Sale_Date"])
                .map_elements(
                    lambda row: convert_to_eur_historical(row["Proceeds"], row["Currency"], row["Last_Sale_Date"])
                )
                .alias("Proceeds_EUR")
            ]
        )
        return df

    @staticmethod
    def get_data_with_id(lines: list, id: str):
        filtered_lines = [line.strip() for line in lines if line.strip().split(",")[0].strip() == id]

        header = next(csv.reader([filtered_lines[0]]))
        rows = list(csv.reader(filtered_lines[1:]))

        df = pl.DataFrame(data=rows, schema=header, orient="row")
        return df
