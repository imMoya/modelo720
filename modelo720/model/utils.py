"""module to build the global model from degiro data."""

from pathlib import Path
from typing import Literal

import polars as pl

from modelo720.config import setup_logging
from modelo720.degiro.reader import DegiroReader

from .references import DEGIRO, GLOBAL_INFO

logger = setup_logging()


class DegiroGlobal:
    """Main class to transform degiro into global model."""

    def __init__(self, file_path: str | Path):
        """Initializes the class with the input file paths.

        Args:
            file_path (Union[str, Path]): file path of the portfolio
        """
        self.df = DegiroReader(file_path).data

    @property
    def data(self):
        """Returns the data property.

        Returns:
            pl.DataFrame: global dataframe
        """
        self._data = self.df.select(DEGIRO["columns"])
        self._data = self.remove_null_values(self._data, "isin")
        self._data = self.add_broker_code(self._data, "degiro")
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

    def generate_financial_record(self) -> str:
        """Generates the financial record for the model 720.

        Returns:
            str: model 720 financial record
        """
        output = []

        data = self.data
        declared_values = self.get_count(data)
        print(self.data)
        total_amount = self.data["eur_value"].sum()
        print(total_amount)
        # Generate header record (17 record)
        header = (
            f"1720"
            f"{GLOBAL_INFO['year']}"
            f"{GLOBAL_INFO['dni_number']}"
            f"{f'{GLOBAL_INFO["surnames"]} {GLOBAL_INFO["name"]}'.ljust(40)}"
            f"T{GLOBAL_INFO['telephone']}"
            f"{f'{GLOBAL_INFO["surnames"]} {GLOBAL_INFO["name"]}'.ljust(40)}"
            f"{7200000000000:013d}"
            f"{' ' * 2}"
            f"{declared_values:022}"
            f"{' ' * 1}"
            f"{int(total_amount * 100):017}"
            f"{' ' * 1}"
            f"{0:017}"
        )
        output.append(header)

        # Generate transaction records (27 records)
        for row in data.to_dicts():
            transaction_sub1 = (
                f"2720"
                f"{GLOBAL_INFO['year']}"
                f"{GLOBAL_INFO['dni_number']}"
                f"{GLOBAL_INFO['dni_number']}"
                f"{' ' * 9}"
                f"{f'{GLOBAL_INFO["surnames"]} {GLOBAL_INFO["name"]}'.ljust(40)}"
                "1"
                f"{' ' * 25}"
                "V1"
                f"{' ' * 25}"
                f"{row['broker_country_id']}"
                "1"
                f"{row['isin']}"
                f"{' ' * 46}"
                f"{row['product']:40}"
            )
            transaction_sub2 = (
                f"{row['isin'][:2]}"
                f"{0:08}A{0:08}"
                " "
                f"{int(row['eur_value'] * 100):014}"
                " "
                f"{0:014}A{int(row['amount'] * 100):012}"
                " "
                f"{int(100 * 100):05}"
            )
            output.append(transaction_sub1)
            output.append(transaction_sub2)

        return "\n".join(output)

    @staticmethod
    def get_count(df: pl.DataFrame) -> int:
        """Returns the count of the dataframe.

        Args:
            df (pl.DataFrame): polars dataframe

        Returns:
            int: count of the dataframe
        """
        return len(df)

    @staticmethod
    def add_broker_code(df: pl.DataFrame, broker: Literal["ibkr", "degiro"]) -> pl.DataFrame:
        """Add to a dataframe an identification of country for the broker.

        Args:
            df (pl.DataFrame): Original dataframe.
            broker (Literal['ibkr', 'degiro']): The broker reference, either 'degiro' or 'ibkr'.

        Returns:
            pl.DataFrame: Modified dataframe with broker_country_id column.
        """
        broker_map = {"degiro": "NL", "ibkr": "IE"}

        if broker not in broker_map:
            raise ValueError(f"Invalid broker reference '{broker}'. Must be 'degiro' or 'ibkr'.")

        return df.with_columns(pl.lit(broker_map[broker]).alias("broker_country_id"))
