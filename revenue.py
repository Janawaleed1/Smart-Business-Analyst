import pandas as pd


def get_total_revenue(file_path):
    df = pd.read_csv(file_path)

    total_revenue = df["Sales"].sum()

    return total_revenue


if __name__ == "__main__":
    file_path = "data/supermart.csv"

    total_revenue = get_total_revenue(file_path)

    print("Total Revenue:", total_revenue)