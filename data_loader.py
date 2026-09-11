import pandas as pd


def load_data(file_path):
    df = pd.read_csv(file_path)

    print("Data loaded successfully!")
    print()

    print("Number of rows:", len(df))
    print("Number of columns:", len(df.columns))
    print()

    print("Columns:")
    print(df.columns.tolist())
    print()

    print("First 5 rows:")
    print(df.head())
    print()

    print("Missing values:")
    print(df.isnull().sum())

    return df


if __name__ == "__main__":
    file_path = "data/supermart.csv"
    df = load_data(file_path)