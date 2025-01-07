from modelo720.degiro.reader import DegiroReader
import polars as pl
from pathlib import Path
from typing import Optional, Union
from .references import DEGIRO
from modelo720.config import setup_logging


logger = setup_logging()


class DegiroGlobal:
    """Main class to transform degiro into global model."""
    def __init__(self, file_path: Union[str, Path]):
        """Initializes the class with the input file paths.

        Args:
            file_path (Union[str, Path]): file path of the portfolio
        """
        self.df = DegiroReader(file_path).data

    @property
    def data(self):
        self._data = self.df.select(DEGIRO["columns"])
        self._data = self.remove_null_values(self._data, "isin")
        return self._data
    
    @staticmethod
    def remove_null_values(df: pl.DataFrame, col_filter: str) -> pl.DataFrame:
        """Removes null values from the dataframe.

        Args:
            df (pl.DataFrame): polars dataframe
            col_filter(str): column to filter

        Returns:
            pl.DataFrame: dataframe without null values
        """
        deleted_df = df.filter(pl.col(col_filter).is_null())
        logger.info(f"Removing the following values: {deleted_df}")
        logger.info("The above values will not be included in the model")
        return df.filter(pl.col(col_filter).is_not_null())
    