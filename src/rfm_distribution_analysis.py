import pandas as pd

from src.rfm_analysis import build_rfm_table


CSV_PATH = "data/processed/cleaned_sales.csv"


def analyze_score_ranges(rfm):
    """
    分析RFM指标五分位范围
    """

    print("\n====================")
    print("Recency Distribution")
    print("====================")

    print(
        rfm["Recency"]
        .describe(
            percentiles=[
                0.2,
                0.4,
                0.6,
                0.8
            ]
        )
    )


    print("\n====================")
    print("Frequency Distribution")
    print("====================")

    print(
        rfm["Frequency"]
        .describe(
            percentiles=[
                0.2,
                0.4,
                0.6,
                0.8
            ]
        )
    )


    print("\n====================")
    print("Monetary Distribution")
    print("====================")

    print(
        rfm["Monetary"]
        .describe(
            percentiles=[
                0.2,
                0.4,
                0.6,
                0.8
            ]
        )
    )


def analyze_revenue_contribution(rfm):

    print("\n====================")
    print("Revenue Contribution")
    print("====================")


    rfm_sorted = (
        rfm
        .sort_values(
            "Monetary",
            ascending=False
        )
        .copy()
    )


    total_revenue = (
        rfm_sorted["Monetary"]
        .sum()
    )


    for pct in [0.05,0.1,0.2]:

        customers = int(
            len(rfm_sorted)*pct
        )

        revenue = (
            rfm_sorted
            .head(customers)["Monetary"]
            .sum()
            /
            total_revenue
            *
            100
        )


        print(
            f"Top {pct*100:.0f}% customers revenue:"
            f" {revenue:.2f}%"
        )


def main():

    df = pd.read_csv(
        CSV_PATH,
        dtype={
            "InvoiceNo":str,
            "StockCode":str
        }
    )


    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"]
    )


    rfm = build_rfm_table(df)


    print(
        "Customer Count:",
        len(rfm)
    )


    analyze_score_ranges(rfm)

    analyze_revenue_contribution(rfm)


if __name__ == "__main__":
    main()