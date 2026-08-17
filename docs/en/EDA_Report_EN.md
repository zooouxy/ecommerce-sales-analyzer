# Exploratory Data Analysis Report


## 1. Project Overview


### 1.1 Background


This project analyzes the Online Retail transaction dataset.

The purpose of Exploratory Data Analysis (EDA) is to understand the dataset structure, identify data quality issues, and provide guidance for data cleaning and business analysis.


The objectives of EDA include:

- Understanding dataset structure
- Evaluating data quality
- Detecting abnormal records
- Exploring transaction characteristics
- Designing data cleaning strategies



---

# 2. Dataset Overview


## 2.1 Data Source


Dataset:

Online Retail.xlsx


The dataset contains transaction records from an online retail business.


It includes:

- Product information
- Order information
- Customer information
- Country information
- Transaction timestamps



---

## 2.2 Dataset Size


Original dataset:

|Metric|Value|
|-|-:|
|Records|541,909|
|Columns|8|



---

# 3. Feature Description


|Feature|Type|Description|
|-|-|-|
|InvoiceNo|Object|Transaction identifier|
|StockCode|Object|Product identifier|
|Description|Object|Product name|
|Quantity|Integer|Purchased quantity|
|InvoiceDate|Datetime|Transaction timestamp|
|UnitPrice|Float|Product price|
|CustomerID|Float|Customer identifier|
|Country|Object|Customer country|



---

# 4. Data Quality Analysis


## 4.1 Missing Value Analysis


Missing values:


|Column|Missing Count|
|-|-:|
|Description|1454|
|CustomerID|135080|



---

## 4.1.1 Missing Product Description


The Description column contains 1,454 missing values.


Since product descriptions are required for:

- Product ranking
- Product analysis
- Product insights


records without descriptions should be removed.



---

## 4.1.2 Missing Customer ID


The CustomerID column contains 135,080 missing values.


Possible reasons:

- Guest customers
- Historical data limitations


CustomerID is not mandatory for transaction-level analysis.

Therefore, missing CustomerID records are retained.



---

# 5. Numerical Feature Analysis


## 5.1 Quantity Analysis


The Quantity column contains negative values.


Possible business meanings:

- Product returns
- Cancelled transactions


Cleaning rule:


Keep records where:

Quantity > 0



---

## 5.2 Unit Price Analysis


The UnitPrice column contains negative values.


Negative prices are invalid in normal sales transactions.


Cleaning rule:


Keep records where:

UnitPrice > 0



---

# 6. Transaction Structure Analysis


The dataset is transaction-level data.


One invoice may contain multiple products.


Therefore:

Number of rows ≠ Number of orders


Order count should be calculated using:

Unique InvoiceNo values.



---

# 7. Data Cleaning Strategy


Based on EDA findings:


|Issue|Treatment|
|-|-|
|Missing Description|Remove records|
|Negative Quantity|Remove records|
|Negative UnitPrice|Remove records|
|Duplicate records|Check and handle|
|Sales calculation|Sales = Quantity × UnitPrice|



---

# 8. Key EDA Findings


EDA identified several important characteristics:


1. The dataset contains more than 540,000 transaction records.


2. The dataset provides multiple analytical dimensions including products, customers, orders and markets.


3. CustomerID has a significant amount of missing information.


4. Quantity and UnitPrice contain invalid negative values.


5. After cleaning, the dataset can support sales analysis and business intelligence tasks.



---

# 9. Conclusion


EDA provided a comprehensive understanding of the raw transaction dataset.


Based on EDA findings, a data cleaning pipeline was developed:


Raw Data

↓

Data Quality Processing

↓

Clean Analytical Dataset

↓

Business Analysis


EDA established the foundation for further sales analytics and business insights.