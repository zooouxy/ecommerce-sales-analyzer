import pandas as pd
import numpy as np

from src.business_rules import (
    RECENCY_RULES,
    FREQUENCY_RULES,
    MONETARY_RULES,
    SEGMENT_RULES
)


def calculate_recency(df):
    """
    计算客户距离最近一次购买的天数。
    """

    reference_date = df["InvoiceDate"].max()

    last_purchase = (
        df.groupby("CustomerID")["InvoiceDate"]
        .max()
    )

    recency = (
        reference_date - last_purchase
    ).dt.days

    return recency.sort_values()


def calculate_frequency(df):
    """
    计算客户购买频率（订单数量）。
    """

    frequency = (
        df.groupby("CustomerID")["InvoiceNo"]
        .nunique()
    )

    return frequency.sort_values(
        ascending=False
    )


def calculate_monetary(df):
    """
    计算客户累计消费金额。
    """

    monetary = (
        df.groupby("CustomerID")["Sales"]
        .sum()
    )

    return monetary.sort_values(
        ascending=False
    )

def apply_recency_score(days):
    """
    根据业务规则计算 Recency Score。
    """

    for rule in RECENCY_RULES:
        if rule["max_days"] is None:
            return rule["score"]

        if days <= rule["max_days"]:
            return rule["score"]


def apply_frequency_score(orders):
    """
    根据业务规则计算 Frequency Score。
    """

    for rule in FREQUENCY_RULES:
        if rule["min_orders"] is None:
            return rule["score"]

        if orders >= rule["min_orders"]:
            return rule["score"]


def apply_monetary_score(amount):
    """
    根据业务规则计算 Monetary Score。
    """

    for rule in MONETARY_RULES:
        if rule["min_amount"] is None:
            return rule["score"]

        if amount >= rule["min_amount"]:
            return rule["score"]

def build_rfm_table(df):
    """
    构建 RFM 基础表。
    """

    recency = calculate_recency(df)
    frequency = calculate_frequency(df)
    monetary = calculate_monetary(df)

    rfm = pd.concat(
        [
            recency.rename("Recency"),
            frequency.rename("Frequency"),
            monetary.rename("Monetary")
        ],
        axis=1
    )

    rfm = rfm.dropna()

    return rfm


def calculate_rfm_scores(rfm):
    """
    根据 business_rules.py 中定义的业务阈值计算 RFM Score。
    """

    rfm = rfm.copy()

    rfm["Monetary"] = rfm["Monetary"].round(2)

    rfm["R_Score"] = (
        rfm["Recency"]
        .apply(apply_recency_score)
    )

    rfm["F_Score"] = (
        rfm["Frequency"]
        .apply(apply_frequency_score)
    )

    rfm["M_Score"] = (
        rfm["Monetary"]
        .apply(apply_monetary_score)
    )

    rfm["R_Score"] = rfm["R_Score"].astype(int)
    rfm["F_Score"] = rfm["F_Score"].astype(int)
    rfm["M_Score"] = rfm["M_Score"].astype(int)

    rfm["RFM_Score"] = (
        rfm["R_Score"]
        +
        rfm["F_Score"]
        +
        rfm["M_Score"]
    )

    return rfm


def assign_customer_segment(rfm):
    """
    根据 business_rules.py 中定义的 Segment Rules 分类。
    """

    def segment_customer(row):

        if (
            row["R_Score"] == 5
            and row["F_Score"] == 5
            and row["M_Score"] == 5
        ):
            return "Champions"


        elif (
            row["R_Score"] >= 4
            and row["F_Score"] >= 4
        ):
            return "Loyal Customers"


        elif (
            row["R_Score"] >= 4
            and row["M_Score"] == 5
            and row["F_Score"] <= 3
        ):
            return "Big Spenders"


        elif (
            row["R_Score"] <= 2
            and row["M_Score"] >= 4
        ):
            return "High Value Lost"


        elif (
            row["R_Score"] <= 2
            and row["F_Score"] >= 3
        ):
            return "At Risk"


        elif (
            row["R_Score"] <= 2
            and row["F_Score"] <= 2
            and row["M_Score"] <= 2
        ):
            return "Lost Customers"


        else:
            return "Regular Customers"


    rfm["Segment"] = (
        rfm.apply(
            segment_customer,
            axis=1
        )
    )

    return rfm

def summarize_customer_segments(rfm):
    """
    汇总客户分群业务指标。
    """

    segment_summary = (
        rfm.groupby("Segment")
        .agg(
            Customer_Count=(
                "Monetary",
                "count"
            ),
            Total_Revenue=(
                "Monetary",
                "sum"
            )
        )
    )


    total_revenue = (
        segment_summary["Total_Revenue"]
        .sum()
    )


    segment_summary["Revenue_Percentage"] = (
        segment_summary["Total_Revenue"]
        /
        total_revenue
        *
        100
    )


    segment_summary[
        "Average_Revenue_Per_Customer"
    ] = (
        segment_summary["Total_Revenue"]
        /
        segment_summary["Customer_Count"]
    )


    return segment_summary.sort_values(
        "Total_Revenue",
        ascending=False
    )