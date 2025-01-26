"""module to build the global model from degiro data."""

from pathlib import Path
from typing import Literal, Optional

import polars as pl
from pydantic.dataclasses import dataclass

from modelo720.config import setup_logging
from modelo720.degiro.reader import DegiroReader
from modelo720.ibkr.reader import IbkrReader

from .references import BROKER_MAP, GLOBAL_INFO

logger = setup_logging()


@dataclass
class FileConfig:
    """Configuration dataclass for broker information."""

    file_path: str | Path
    broker: Literal["ibkr", "degiro"]
    presented: bool
    year: int


class GlobalCompute:
    """Main class to transform data into global model."""

    def __init__(self, configs: list[FileConfig], prev_configs: Optional[list[FileConfig]] = None):
        """Initializes the class with the configuration.

        Args:
            config (list[FileConfig]): List of configuration objects containing broker details.
        self.df = self._load_data(file_path, broker)
        """
        self.config = configs
        self.dataframes = [self._load_data(config) for config in configs]
        self.old_dataframes = [self._load_data(config) for config in prev_configs] if prev_configs else []
        #self.concat_data = self._concat_data()

    def _load_data(self, config: FileConfig) -> pl.DataFrame:
        """Loads data based on the broker type specified in the configuration.

        Args:
            config (FileConfig): Configuration object containing broker details.

        Returns:
            pl.DataFrame: Loaded data as a Polars DataFrame.

        Raises:
            ValueError: If the broker type is invalid.
        """
        broker = config.broker
        file_path = config.file_path

        if broker == "degiro":
            reader = DegiroReader(file_path)
        elif broker == "ibkr":
            reader = IbkrReader(file_path, 2023)
        else:
            raise ValueError(f"Unsupported broker type: {broker}")

        logger.info(f"Loaded data for broker: {broker} | Presented: {config.presented}")
        df = reader.data.select(BROKER_MAP[broker]["columns"])
        df = self.remove_null_values(df, "isin")
        df = self.add_broker_code(df, config.broker)
        print(df)
        return df

    @staticmethod
    def _concat_data(dataframes_list = list[pl.DataFrame]) -> pl.DataFrame:
        """Concatenates a list of Polars DataFrames into a single DataFrame.

        Args:
            dataframes_list (list[pl.DataFrame]): A list of Polars DataFrames to concatenate.

        Returns:
            pl.DataFrame: A single concatenated Polars DataFrame.
        """
        return pl.concat(dataframes_list)

    @property
    def data(self) -> pl.DataFrame:
        """Returns the concatenated data property.

        Returns:
            pl.DataFrame: Concatenated dataframe.
        """
        return self.concat_data(self.dataframes)
    
    @property
    def old_data(self) -> pl.DataFrame:
        """Returns the concatenated old data property.

        Returns:
            pl.DataFrame: Concatenated dataframe.
        """
        return self.concat_data(self.old_dataframes) 

    @property
    def financial_record(self) -> str:
        return "\n".join(self.generate_financial_record())

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

    @staticmethod
    def add_broker_code(df: pl.DataFrame, broker: Literal["ibkr", "degiro"]) -> pl.DataFrame:
        """Add to a dataframe an identification of country for the broker.

        Args:
            df (pl.DataFrame): Original dataframe.
            broker (Literal['ibkr', 'degiro']): The broker reference, either 'degiro' or 'ibkr'.

        Returns:
            pl.DataFrame: Modified dataframe with broker_country_id column.
        """
        broker_map = {broker: info["country"] for broker, info in BROKER_MAP.items()}

        if broker not in broker_map:
            raise ValueError(f"Invalid broker reference '{broker}'. Must be 'degiro' or 'ibkr'.")

        return df.with_columns(pl.lit(broker_map[broker]).alias("broker_country_id"))

    def generate_financial_record(self) -> str:
        """Generates the financial record for the model 720.

        Returns:
            str: model 720 financial record
        """
        output = []

        data = self.data
        declared_values = self.get_count(data)
        total_amount = data["eur_value"].sum()

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

        # Generate transaction records (27 record)
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

        return output

    @staticmethod
    def get_count(df: pl.DataFrame) -> int:
        """Returns the count of the dataframe.

        Args:
            df (pl.DataFrame): polars dataframe

        Returns:
            int: count of the dataframe
        """
        return len(df)
