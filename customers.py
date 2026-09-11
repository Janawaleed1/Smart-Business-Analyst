import pandas as pd


def get_customer_statistics(file_path):
    df = pd.read_csv(file_path)

    customer_statistics = (
        df.groupby("Customer Name")
        .agg(
            Total_Sales=("Sales", "sum"),
            Number_of_Orders=("Order ID", "nunique"),
            Average_Order_Value=("Sales", "mean")
        )
        .sort_values("Total_Sales", ascending=False)
        .reset_index()
    )

    return customer_statistics


if __name__ == "__main__":
    file_path = "data/supermart.csv"

    customer_statistics = get_customer_statistics(file_path)

    print("Customer Statistics:")
    print(customer_statistics.head(10))