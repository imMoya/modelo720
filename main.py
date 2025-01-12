"""Main program."""
from modelo720 import DegiroReader, IbkrReader
from modelo720 import DegiroGlobal

def main():
    """Main program."""
    df_prev = DegiroReader("datasets/Portfolio2023.csv").data
    df_curr = DegiroReader("datasets/Portfolio2024.csv").data
    print(df_prev)
    print(df_curr)


if __name__ == "__main__":
    #main()
    print(DegiroGlobal("datasets/Portfolio2023.csv").generate_financial_record())
    print(IbkrReader("datasets/Portfolio2023_IBKR.csv", 2023).data)
   
    from currency_converter import CurrencyConverter
    from datetime import datetime
    curr_conv = CurrencyConverter()
    historical_date = datetime.strptime("2023-12-29", "%Y-%m-%d")
    print(curr_conv.convert(100, 'USD', 'EUR', historical_date))