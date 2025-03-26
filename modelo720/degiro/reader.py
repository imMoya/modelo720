"""degiro reader for modelo720."""

from pathlib import Path

import polars as pl

from modelo720.utils import try_float

from .references import COLUMNS_DICT, DESIRED_SCHEMA


class DegiroReader:
    """Reads the Degiro portfolio CSV file."""

    def __init__(self, file_path: str | Path):
        """Initializes class to read CSV.

        Args:
            file_path (Union[str, Path]): file path of the portfolio
        """
        self.file_path = Path(file_path)

    @property
    def data(self):
        """Performs data transformations."""
        self._data = self.read_dataset()
        self._data = self._data.rename(COLUMNS_DICT).select(list(COLUMNS_DICT.values()))
        self._data = self.split_local_value(self._data)
        self._data = self.convert_num_columns(self._data)
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
            if df[col].dtype == pl.Float64:
                continue

            if df[col].dtype == pl.Int64:
                df = df.with_columns(pl.col(col).cast(pl.Float64).alias(col))

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

    @staticmethod
    def split_local_value(df: pl.DataFrame, col_name: str = "local_value") -> pl.DataFrame:
        """Split local value into currency and value.

        Args:
            df (pl.DataFrame): polars dataframe
            col_name (str, optional): column name. Defaults to "local_value".

        Returns:
            pl.DataFrame: reformatted polars dataframe with split columns
        """
        return df.with_columns(
            pl.col(col_name)
            .str.extract_groups(r"(\w+)\s+([\d,\.]+)")
            .struct.rename_fields(["local_curr", "local_value"])
            .alias(col_name),
        ).unnest(col_name)
