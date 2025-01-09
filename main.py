"""Main program."""
from modelo720 import DegiroReader
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


    
