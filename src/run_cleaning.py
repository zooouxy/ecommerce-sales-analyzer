import pandas as pd

from src.data_cleaner import clean_sales_data


# Load raw data
df = pd.read_excel(
    "data/raw/Online Retail.xlsx"
)


# Clean data
cleaned_df = clean_sales_data(df)


# Save processed data
cleaned_df.to_csv(
    "data/processed/cleaned_sales.csv",
    index=False
)

print("Cleaning completed!")
print(cleaned_df.shape)