# Data Cleaning Report


# 1. Cleaning Objective


The objective of this stage is to transform raw transaction data into a reliable analytical dataset.


The cleaning process focuses on:

- Missing values
- Invalid transactions
- Incorrect prices
- Data consistency issues


The final output:

cleaned_sales.csv


is used for downstream sales analytics.



---

# 2. Input Dataset


Input file:

Online Retail.xlsx


Original dataset:


|Metric|Value|
|-|-:|
|Records|541909|
|Columns|8|



---

# 3. Data Quality Issues


## 3.1 Missing Product Description


Issue:

The Description column contains missing values.


Missing records:

1454


Impact:

Missing product information affects product-level analysis.


Treatment:

Remove records with missing Description.



---

## 3.2 Invalid Quantity


Issue:

Negative Quantity values exist.


Possible reasons:

- Product returns
- Cancelled orders


Cleaning rule:

Keep records where:

Quantity > 0



---

## 3.3 Invalid Unit Price


Issue:

Negative UnitPrice values exist.


Reason:

Product prices should not be negative in normal transactions.


Cleaning rule:

Keep records where:

UnitPrice > 0



---

# 4. Data Cleaning Pipeline


Process:


Raw Excel Dataset

↓

Load Data

↓

Remove Missing Product Description

↓

Filter Invalid Quantity

↓

Filter Invalid Unit Price

↓

Generate Sales Metric

↓

Export CSV



---

# 5. Data Transformation


## 5.1 Sales Feature Creation


New feature:

Sales


Formula:


Sales = Quantity × UnitPrice


Used for:

- Revenue calculation
- Product analysis
- Country analysis



---

# 6. Data Validation


Validation includes:


## Data Completeness

Check:

- Missing product descriptions


## Numerical Validity

Check:

- Quantity > 0
- UnitPrice > 0


## Data Types

Ensure:

- InvoiceDate is datetime
- Numerical columns maintain correct types



---

# 7. Output Dataset


Output:

cleaned_sales.csv


Used for:

- KPI analysis
- Product analysis
- Market analysis
- Time trend analysis



---

# 8. Conclusion


The data cleaning pipeline successfully transformed raw transaction records into a reliable analytical dataset.


The processed dataset provides a strong foundation for business analysis and visualization.