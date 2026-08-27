# AI Ecommerce Analyst System Architecture

## 1. Project Overview

AI Ecommerce Analyst is an intelligent business analytics system designed for ecommerce decision support.
The system combines analytical pipelines, LLM reasoning, and future agent-based workflows.

## 2. System Architecture

The system follows a modular layered architecture:

```text
User
  |
  v
AI Agent
  |
  v
Tool / Query Service Layer
  |
  v
Analytics Layer
  |
  +----------------------+
  |                      |
  v                      v
Python Analytics     SQL / View Layer
                         |
                         v
                    Data Layer
```

The SQL / View Layer contains stable and reusable business logic so that Query Service and Agent layers do not need to repeatedly reimplement complex analytical rules.

## 3. Architecture Layers

### Data Layer

Responsible for business data storage and management.

Current core database objects include:

Base tables:
- customers
- products
- orders
- order_items

Analytical views:
- customer_rfm_base
- customer_rfm_scores
- customer_segments

These Views transform transactional data into stable analytical models that can be queried directly by business services and future Agents.

### Analytics Layer

Responsible for deterministic business computations and analytics.

Current capabilities include:
- Sales KPIs
- Monthly sales trends
- Customer value analysis
- Product performance
- Product revenue concentration
- RFM analysis
- Customer segmentation

The Python analytics layer is mainly used for analytical development, validation, and debugging.
The SQL / View layer is used for stable querying, service access, and Agent integration.

### Business Rule Layer

Responsible for centralized management of validated business rules.

Current rule source:

```text
src/business_rules.py
```

It includes:
- RFM Recency scoring rules
- RFM Frequency scoring rules
- RFM Monetary scoring rules
- Customer Segment definitions

Target architecture:

```text
Business Rules
      |
      +------> Python Analytics
      |
      +------> SQL Views
      |
      +------> Query Service / Agent
```

This reduces duplicated business logic and lowers the risk of inconsistent results across Python, SQL, and Agent outputs.

### Tool / Query Service Layer

Exposes analytical capabilities through standardized interfaces.

Responsibilities include:
- Loading standardized SQL queries
- Querying analytical Views
- Supporting parameterized business queries
- Returning structured results to the Agent layer

The Agent does not need to recalculate RFM or customer segments. It queries validated analytical models instead.

### LLM Layer

Responsible for:
- Semantic understanding
- Business question interpretation
- Result explanation
- Insight and recommendation generation

The LLM does not perform core deterministic calculations.

### RAG Layer

Provides domain knowledge augmentation, including:
- Data dictionary
- Business Rules
- Metric definitions
- Project documentation
- Future domain knowledge sources

### Agent Layer

Coordinates tasks and tool execution.

The Agent maps user questions to the appropriate analytical capability and converts structured results into natural-language business answers.

## 4. Data Flow

Current core data flow:

```text
Raw Data
Online Retail.xlsx
        |
        v
Data Cleaning
src/data_cleaner.py
        |
        v
cleaned_sales.csv
        |
        v
Database ETL
src/load_database.py
        |
        v
SQLite Base Tables
customers / products / orders / order_items
        |
        v
Database Views
customer_rfm_base
        |
        v
customer_rfm_scores
        |
        v
customer_segments
        |
        v
Query Service
        |
        v
Agent
        |
        v
Business Answer
```

After loading base tables, `src/load_database.py` automatically executes the View SQL files stored under `database/views/`.

## 5. RFM Data Model

The RFM module uses layered database Views to reduce duplicated SQL logic.

### customer_rfm_base

Purpose:

Calculates customer-level RFM base metrics:

```text
customer_id
recency_days
frequency
monetary
```

Business question:

> What is each customer's historical purchasing behavior?

### customer_rfm_scores

Input:

```text
customer_rfm_base
```

Purpose:

Generates validated customer scores:

```text
r_score
f_score
m_score
rfm_code
rfm_score
```

Business question:

> How can customer purchasing behavior be converted into comparable customer value scores?

### customer_segments

Input:

```text
customer_rfm_scores
```

Purpose:

Classifies customers into:
- Champions
- Loyal Customers
- Big Spenders
- High Value Lost
- At Risk
- Lost Customers
- Regular Customers

Business question:

> Which business action should be applied to each customer group?

## 6. Python and SQL Consistency Validation

The project includes:

```text
src/check_rfm_consistency.py
```

to compare:

```text
Pandas RFM Result
        VS
SQLite View Result
```

Validation covers:
- Customer count
- Recency
- Frequency
- Monetary
- R Score
- F Score
- M Score
- RFM Score
- Customer Segment

Current result:

```text
RFM reconciliation result:
PASS
```

This ensures that the Python analytics layer and SQL View layer produce consistent customer analytics results.

## 7. Agent Query Execution Flow

Example question:

> What percentage of customers are Loyal Customers?

Execution flow:

```text
User Question
      |
      v
Agent / LLM
      |
      v
Query Service
      |
      v
SELECT ... FROM customer_segments
      |
      v
SQLite View Chain
customer_segments
      |
      v
customer_rfm_scores
      |
      v
customer_rfm_base
      |
      v
orders + order_items
      |
      v
Structured Result
      |
      v
Natural Language Answer
```

This design keeps complex business calculations inside stable analytical models while the Agent focuses on understanding user intent and selecting the correct query.

## 8. Design Principles

### Separation of Computation and Reasoning

Python / SQL:
- Data processing
- Metric calculation
- Statistical analysis
- Business rule execution

LLM:
- Semantic understanding
- Business interpretation
- Recommendation generation

### Single Source of Business Rules

Business rules are centrally managed in:

```text
src/business_rules.py
```

Consistency tests ensure that SQL Views remain aligned with the Python implementation.

### Layered Decoupling

The system follows:

```text
Storage
   ↓
View / Modeling
   ↓
Analytics
   ↓
Query Service
   ↓
Agent
```

This reduces coupling and improves testability and maintainability.

### Explainability

Core business metrics and customer segments are generated by deterministic rules instead of direct LLM inference.

## 9. Extensibility

The architecture supports future integration of:
- SQL Query Tools
- Analytics Skills
- Knowledge Retrieval Systems
- Agent Workflows
- Dashboard / BI Layer
- API Services
- Multi-database Support
