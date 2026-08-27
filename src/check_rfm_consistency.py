import sqlite3
import pandas as pd

from src.rfm_analysis import (
    build_rfm_table,
    calculate_rfm_scores,
    assign_customer_segment
)


CSV_PATH = "data/processed/cleaned_sales.csv"
DB_PATH = "database/ecommerce.db"


# ===============================
# 字段统一
# ===============================

def normalize_columns(df):
    """
    统一 Pandas RFM 字段名称，使其与 SQL 层保持一致。
    """

    column_mapping = {
        "CustomerID": "customer_id",
        "Recency": "recency_days",
        "Frequency": "frequency",
        "Monetary": "monetary",
        "R_Score": "r_score",
        "F_Score": "f_score",
        "M_Score": "m_score",
        "RFM_Score": "rfm_score",
        "Segment": "segment"
    }

    return df.rename(columns=column_mapping)


# ===============================
# Load source data
# ===============================

df = pd.read_csv(
    CSV_PATH,
    dtype={
        "InvoiceNo": str,
        "StockCode": str
    }
)

df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"]
)


# ===============================
# Pandas RFM
# ===============================

pandas_rfm = build_rfm_table(df)

pandas_rfm = calculate_rfm_scores(
    pandas_rfm
)

pandas_rfm = assign_customer_segment(
    pandas_rfm
)

pandas_rfm = pandas_rfm.reset_index()

pandas_rfm = normalize_columns(
    pandas_rfm
)

pandas_rfm["customer_id"] = (
    pandas_rfm["customer_id"]
    .astype(int)
)


pandas_check = pandas_rfm[
    [
        "customer_id",
        "recency_days",
        "frequency",
        "monetary",
        "r_score",
        "f_score",
        "m_score",
        "rfm_score",
        "segment"
    ]
].copy()


pandas_check["monetary"] = (
    pandas_check["monetary"]
    .round(2)
)


# ===============================
# SQL RFM
# ===============================

conn = sqlite3.connect(DB_PATH)

sql_check = pd.read_sql_query(
    """
    SELECT
        customer_id,
        recency_days,
        frequency,
        monetary,
        r_score,
        f_score,
        m_score,
        rfm_score,
        segment
    FROM customer_segments
    """,
    conn
)

conn.close()


sql_check["customer_id"] = (
    sql_check["customer_id"]
    .astype(int)
)

sql_check["monetary"] = (
    sql_check["monetary"]
    .round(2)
)


# ===============================
# Merge validation
# ===============================

comparison = pandas_check.merge(
    sql_check,
    on="customer_id",
    how="outer",
    suffixes=(
        "_pandas",
        "_sql"
    ),
    indicator=True
)


# ===============================
# Customer count
# ===============================

print("Pandas customers:",
      len(pandas_check))

print("SQL customers:",
      len(sql_check))


missing_in_sql = (
    comparison["_merge"]
    == "left_only"
).sum()


missing_in_pandas = (
    comparison["_merge"]
    == "right_only"
).sum()


print(
    "Missing in SQL:",
    missing_in_sql
)

print(
    "Missing in Pandas:",
    missing_in_pandas
)


# ===============================
# Raw RFM validation
# ===============================


comparison["recency_diff"] = (
    comparison["recency_days_pandas"]
    -
    comparison["recency_days_sql"]
)


comparison["frequency_diff"] = (
    comparison["frequency_pandas"]
    -
    comparison["frequency_sql"]
)


comparison["monetary_diff"] = (
    comparison["monetary_pandas"]
    -
    comparison["monetary_sql"]
)



print("\nRaw RFM differences:")

print(
    "Recency:",
    (comparison["recency_diff"] != 0).sum()
)


print(
    "Frequency:",
    (comparison["frequency_diff"] != 0).sum()
)


print(
    "Monetary:",
    (
        comparison["monetary_diff"]
        .abs()
        > 0.01
    ).sum()
)



# ===============================
# Score validation
# ===============================

print("\nScore differences:")


print(
    "R score:",
    (
        comparison["r_score_pandas"]
        !=
        comparison["r_score_sql"]
    ).sum()
)


print(
    "F score:",
    (
        comparison["f_score_pandas"]
        !=
        comparison["f_score_sql"]
    ).sum()
)


print(
    "M score:",
    (
        comparison["m_score_pandas"]
        !=
        comparison["m_score_sql"]
    ).sum()
)


print(
    "RFM score:",
    (
        comparison["rfm_score_pandas"]
        !=
        comparison["rfm_score_sql"]
    ).sum()
)



# ===============================
# Segment validation
# ===============================

segment_diff = (
    comparison["segment_pandas"]
    !=
    comparison["segment_sql"]
).sum()


print(
    "Segment differences:",
    segment_diff
)



# ===============================
# Show mismatches
# ===============================

score_mismatches = comparison[
    (
        comparison["r_score_pandas"]
        !=
        comparison["r_score_sql"]
    )
    |
    (
        comparison["f_score_pandas"]
        !=
        comparison["f_score_sql"]
    )
    |
    (
        comparison["m_score_pandas"]
        !=
        comparison["m_score_sql"]
    )
]


print("\nSample score mismatches:")


if score_mismatches.empty:
    print("None")

else:

    print(
        score_mismatches[
            [
                "customer_id",
                "r_score_pandas",
                "r_score_sql",
                "f_score_pandas",
                "f_score_sql",
                "m_score_pandas",
                "m_score_sql"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )



segment_mismatches = comparison[
    comparison["segment_pandas"]
    !=
    comparison["segment_sql"]
]


print("\nSample segment mismatches:")


if segment_mismatches.empty:

    print("None")

else:

    print(
        segment_mismatches[
            [
                "customer_id",
                "rfm_score_pandas",
                "rfm_score_sql",
                "segment_pandas",
                "segment_sql"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )



# ===============================
# Final result
# ===============================


all_metrics_match = (

    missing_in_sql == 0

    and

    missing_in_pandas == 0

    and

    (comparison["recency_diff"] != 0).sum() == 0

    and

    (comparison["frequency_diff"] != 0).sum() == 0

    and

    (
        comparison["monetary_diff"]
        .abs()
        > 0.01
    ).sum() == 0

    and

    (
        comparison["r_score_pandas"]
        !=
        comparison["r_score_sql"]
    ).sum() == 0

    and

    (
        comparison["f_score_pandas"]
        !=
        comparison["f_score_sql"]
    ).sum() == 0

    and

    (
        comparison["m_score_pandas"]
        !=
        comparison["m_score_sql"]
    ).sum() == 0

    and

    (
        comparison["rfm_score_pandas"]
        !=
        comparison["rfm_score_sql"]
    ).sum() == 0

    and

    segment_diff == 0

)


print("\nRFM reconciliation result:")

print(
    "PASS"
    if all_metrics_match
    else "FAIL"
)