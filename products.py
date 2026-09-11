import pandas as pd


def get_top_products(file_path, top_n=5):
    df = pd.read_csv(file_path)

    top_products = (
        df.groupby("Sub Category")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )

    return top_products


if __name__ == "__main__":
    file_path = "data/supermart.csv"

    top_products = get_top_products(file_path)

    print("Top Products:")
    print(top_products)