"""Main program."""
from modelo720 import DegiroReader


def main():
    """Main program."""
    df = DegiroReader("datasets/Portfolio2023.csv").data
    print(df)


if __name__ == "__main__":
    main()
    
