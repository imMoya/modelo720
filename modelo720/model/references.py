"""references for the model."""

from pydantic import BaseModel, Field


class BrokerInfo(BaseModel):
    name: str
    country: str
    columns: list[str]


class GlobalInfo(BaseModel):
    year: int
    dni_number: str
    surnames: str
    name: str
    telephone: str
    ownership_percentage: float = Field(ge=0, le=100)


DEGIRO = BrokerInfo(
    name="DEGIRO",
    country="NL",
    columns=["product", "isin", "amount", "eur_value"],
)

IBKR = BrokerInfo(
    name="IBKR",
    country="IE",
    columns=["product", "isin", "amount", "eur_value"],
)

BROKER_MAP: dict[str, BrokerInfo] = {"degiro": DEGIRO, "ibkr": IBKR}

GLOBAL_INFO = GlobalInfo(
    year=2024,
    dni_number="00000000T",
    surnames="<SURNAME1 SURNAME2>",
    name="<NAME>",
    telephone="676767676",
    ownership_percentage=100.0,
)
