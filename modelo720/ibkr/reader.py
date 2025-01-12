"""ibkr reader for modelo720."""
import polars as pl
from pathlib import Path
from typing import Union
from modelo720.utils import try_float, convert_to_eur_historical
from .references import COLUMNS_DICT


class IbkrReader:
    """Reads the IBKR portfolio CSV file."""
    def __init__(self, file_path: Union[str, Path]):
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
        #TODO: create a method to build "eur_value" column
        self._data = self._data.with_columns(
            pl.struct(["local_value", "local_currency"]).map_elements(lambda x: convert_to_eur_historical(x["local_value"], x["local_currency"], "2023-12-31"), return_dtype=float)
            .alias("eur_value")
        )
        #self._data = self.convert_num_columns(self._data)
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
                        df = df.with_columns([
                            pl.col(col)
                            .str.replace(',', '.')
                            .cast(pl.Float64)
                            .alias(col)
                        ])
                except Exception:
                    continue
        
        return df
