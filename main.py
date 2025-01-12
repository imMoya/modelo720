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
    my_file = FileConfig("datasets/Portfolio2023.csv", "degiro", True)
    print(GlobalCompute(my_file).generate_financial_record())