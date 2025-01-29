"""Main program."""
from modelo720.degiro import DegiroReader
from modelo720.model.compute import FileConfig, GlobalCompute

def main():
    """Main program."""
    df_prev = DegiroReader("datasets/Portfolio2023.csv").data
    df_curr = DegiroReader("datasets/Portfolio2024.csv").data
    print(df_prev)
    print(df_curr)


if __name__ == "__main__":
    #main()
    #print(DegiroGlobal("datasets/Portfolio2023.csv").generate_financial_record())
    #print(DegiroReader("datasets/Portfolio2023.csv").data)
    #print(IbkrReader("datasets/Portfolio2023_IBKR.csv", 2023).data)
    #my_file = FileConfig("datasets/Portfolio2023.csv", "degiro", True, 2023)
    #print(GlobalCompute(my_file).generate_financial_record())
    length_to_match = len("1720202400000000T<SURNAME1 SURNAME2> <NAME>              T676767676<SURNAME1 SURNAME2> <NAME>              7200000000000")
    files_2023 = [
        FileConfig("datasets/Portfolio2023_IBKR.csv", "ibkr", True, 2023),
        FileConfig("datasets/Portfolio2023.csv", "degiro", True, 2023)
    ]
    files_2024 = [
        FileConfig("datasets/Portfolio2024_IBKR.csv", "ibkr", True, 2023),
        FileConfig("datasets/Portfolio2024.csv", "degiro", True, 2023)
    ]
    a = GlobalCompute(configs=files_2023)
    print(a.generate_financial_record())
    