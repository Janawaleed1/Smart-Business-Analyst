import pandas as pd


def get_monthly_sales(file_path):
    df = pd.read_csv(file_path)

    df["Order Date"] = pd.to_datetime(df["Order Date"], format="mixed")

    monthly_sales = (
        df.groupby(df["Order Date"].dt.to_period("M"))["Sales"]
        .sum()
        .reset_index()
    )

    monthly_sales["Order Date"] = monthly_sales["Order Date"].astype(str)

    return monthly_sales


if __name__ == "__main__":
    file_path = "data/supermart.csv"

    monthly_sales = get_monthly_sales(file_path)

    print("Monthly Sales:")
    print(monthly_sales)