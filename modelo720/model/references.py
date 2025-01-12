"""references for the model."""
DEGIRO = {
    "name": "DEGIRO",
    "country": "NL",
    "columns": ["product", "isin", "amount", "eur_value"],
}
IBKR = {
    "name": "IBKR",
    "country": "IE",
    "columns": ["product", "isin", "amount", "eur_value"],
}

BROKER_MAP = {
    "degiro": DEGIRO,
    "ibkr": IBKR
}

GLOBAL_INFO = {
    "year": "2024",
    "dni_number": "00000000T",
    "surnames": "<SURNAME1 SURNAME2>",
    "name": "<NAME>",
    "telephone": "676767676",
    "ownership_percentage": 100,
}