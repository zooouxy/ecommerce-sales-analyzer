# Business Rules (Frozen Version)

Version: v1.0\
Status: Verified and Frozen

## 1. Data Scope Definition

### 1.1 Revenue Definition

-   Revenue is calculated from transaction-level `Sales`.
-   Sales = Quantity × UnitPrice.
-   All analysis must use the cleaned dataset:

`data/processed/cleaned_sales.csv`

------------------------------------------------------------------------

## 2. Non-Product Transaction Rules

The following transaction types are excluded from product analysis:

  Stock Code     Description
  -------------- -------------------
  DOT            DOTCOM POSTAGE
  POST           POSTAGE
  M              Manual
  AMAZONFEE      AMAZON FEE
  B              ADJUST BAD DEBT
  C2             CARRIAGE
  23444          NEXT DAY CARRIAGE
  BANK CHARGES   BANK CHARGES
  23574          PACKING CHARGE
  S              SAMPLES

Rules:

-   These records represent shipping, fees, adjustments, samples, or
    system transactions.
-   They remain included in overall sales and customer value analysis.
-   They are excluded only from Product Performance and Product
    Concentration analysis.

------------------------------------------------------------------------

## 3. Product Analysis Rules

Product analysis follows these rules:

- `StockCode` is the unique product identifier.
- Before analysis, `StockCode` is standardized by:
  - trimming leading and trailing whitespace;
  - converting values to uppercase.
- `Description` is used only as a display attribute and is not used as the product identifier or aggregation key.
- The 10 defined non-product transaction codes are excluded.
- Revenue is aggregated by `StockCode` and rounded to two decimal places.

Top Product Revenue Share:

Top N Product Revenue / Total Product Revenue × 100

Frozen metrics:

- Top 10 Product Revenue Share = **9.45%**
- Total Product Revenue = **10,270,813.87**
- Top 10 Product Revenue = **970,100.89**

Consistency status:

- Pandas / SQL Product Concentration Consistency: PASS

------------------------------------------------------------------------

## 4. Customer Analysis Rules

Customer ID is the unique customer identifier.

Metrics:

### Recency

Days since the customer's last purchase.

Formula:

Reference Date - Last Purchase Date

Lower values indicate higher activity.

### Frequency

Number of unique orders.

Definition:

COUNT(DISTINCT InvoiceNo)

### Monetary

Total historical customer spending.

Definition:

SUM(Sales)

------------------------------------------------------------------------

## 5. RFM Rules

All RFM metrics use five-level scoring:

-   R Score: Recent customers receive higher scores.
-   F Score: Frequent buyers receive higher scores.
-   M Score: Higher spending customers receive higher scores.

RFM Score:

R Score + F Score + M Score

------------------------------------------------------------------------

## 6. Customer Segment Definitions

Frozen segments:

### Champions

High activity, high frequency, high spending customers.

### Loyal Customers

Stable repeat customers.

### Regular Customers

Normal customers.

### At Risk

Previously valuable customers with declining recent activity.

### Lost Customers

Customers with long inactivity.

### High Value Lost

Historically valuable customers who have likely churned.

### Big Spenders

Customers with exceptionally high spending.

------------------------------------------------------------------------

## 7. Pandas and SQL Consistency Rules

Pandas Layer:

-   Used for developing, testing, and validating analytical logic.

SQL Layer:

-   Used for production queries, Agent access, and application services.

Both layers must maintain:

-   identical filters
-   identical metric definitions
-   identical business logic

------------------------------------------------------------------------

