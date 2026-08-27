AI Ecommerce Analyst Data Dictionary

1. Document Overview
This document defines the data structure, business entities, field definitions, and relationships of the AI Ecommerce Analyst system.

2. Data Domain Model
Core business entities:

Customer: Customer dimension data.
Transaction: Transaction fact data.
Product: Product dimension data.

Relationships:

Customer 1:N Transaction
Product 1:N Transaction

3. Customer Entity
Purpose:
Stores customer profile information.

Fields:
CustomerID | INTEGER | Unique customer identifier
Country | VARCHAR | Customer geographic location

Business usage:
- Customer profiling
- Customer segmentation
- Geographic analysis

4. Transaction Entity
Purpose:
Stores product-level transaction records.

Fields:
InvoiceNo | VARCHAR | Order identifier
InvoiceDate | DATE | Transaction timestamp
CustomerID | INTEGER | Customer reference
StockCode | VARCHAR | Product identifier
Quantity | INTEGER | Purchased quantity
UnitPrice | DECIMAL | Unit price
Sales | DECIMAL | Transaction revenue

Business usage:
- Sales analytics
- Revenue calculation
- Customer value analysis
- Product performance analysis

5. Product Entity
Purpose:
Stores product dimension information.

Fields:
StockCode | VARCHAR | Product identifier
Description | VARCHAR | Product name

Possible extensions:
Category, Supplier, Cost

6. Analytical Views

Database Views encapsulate business logic and provide a consistent
analytical layer for Python analysis, SQL queries, and future Agent
applications.

## customer_rfm_base

Purpose: Generate customer-level RFM base metrics.

Fields: - customer_id: Customer identifier - recency_days: Days since
last purchase - frequency: Number of orders - monetary: Total customer
revenue

## customer_rfm_scores

Purpose: Generate RFM scores based on business thresholds.

### Basis for Scoring Rule Design

This project uses fixed business thresholds instead of dynamic
percentile scoring.

Design principles:

1.  Data distribution analysis: Customer Recency, Frequency, and
    Monetary distributions were analyzed to identify meaningful behavior
    ranges.

2.  Business interpretability: Fixed thresholds are easier for business
    users to understand and apply.

3.  Analytical consistency: The same rules are used across Python, SQL
    Views, and future Agent queries.

4.  Maintainability: Centralized business rules prevent inconsistent
    results across different implementations.

Scoring fields: - r_score - f_score - m_score - rfm_code - rfm_score

Scoring rules:

R Score: - \<=12 days: 5 - 13-32 days: 4 - 33-71 days: 3 - 72-178 days:
2 - \>178 days: 1

F Score: - \>=8 orders: 5 - \>=4 orders: 4 - \>=3 orders: 3 - \>=2
orders: 2 - Otherwise: 1

M Score: - \>=5000: 5 - \>=2000: 4 - \>=800: 3 - \>=300: 2 - Otherwise:
1

## customer_segments

Purpose: Classify customers based on RFM scores.

Segments: - Champions - Loyal Customers - Big Spenders - High Value
Lost - At Risk - Lost Customers - Regular Customers

7. Data Extensibility
Future extensions:

- Customer behavior data
- Product category data
- Marketing campaign data
- Supply chain data