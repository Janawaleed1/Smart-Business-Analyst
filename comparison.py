import pandas as pd


def compare_periods(file_path, period1, period2):
    df = pd.read_csv(file_path)

    df["Order Date"] = pd.to_datetime(
        df["Order Date"],
        format="mixed"
    )

    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month

    def get_period_sales(period):
        year, quarter = period.split("-")

        year = int(year)
        quarter = int(quarter.replace("Q", ""))

        start_month = (quarter - 1) * 3 + 1
        end_month = start_month + 2

        period_data = df[
            (df["Year"] == year)
            & (df["Month"] >= start_month)
            & (df["Month"] <= end_month)
        ]

        return period_data["Sales"].sum()

    sales1 = get_period_sales(period1)
    sales2 = get_period_sales(period2)

    difference = sales2 - sales1

    if sales1 != 0:
        percentage_change = (difference / sales1) * 100
    else:
        percentage_change = 0

    result = {
        "period1": period1,
        "period1_sales": sales1,
        "period2": period2,
        "period2_sales": sales2,
        "difference": difference,
        "percentage_change": percentage_change
    }

    return result


if __name__ == "__main__":
    file_path = "data/supermart.csv"

    result = compare_periods(
        file_path,
        "2017-Q1",
        "2018-Q3"
    )

    print("Period Comparison:")
    print(result)