# AI电商分析系统架构

## 1. 项目概述

AI Ecommerce Analyst 是一个面向电商业务场景的智能商业分析系统。
系统结合数据分析能力、大语言模型能力和未来 Agent 工具调用能力，实现自然语言驱动的业务洞察生成。

## 2. 系统架构设计

系统采用模块化分层架构：

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

SQL / View Layer 用于承载稳定、可复用的业务计算逻辑，避免 Query Service 或 Agent 直接重复实现复杂分析规则。

## 3. 架构层次

### Data Layer

负责业务数据存储和管理。

当前核心数据库对象包括：

基础表：
- customers
- products
- orders
- order_items

分析视图：
- customer_rfm_base
- customer_rfm_scores
- customer_segments

这些 View 将底层交易数据转换为可直接用于业务分析和 Agent 查询的稳定数据模型。

### Analytics Layer

负责确定性指标计算和业务分析。

当前主要包括：
- 销售 KPI
- 月度销售趋势
- 客户价值分析
- 商品表现分析
- 商品收入集中度
- RFM 客户分析
- 客户分群

Python 分析层主要用于分析开发、验证和调试；SQL / View 分析层用于稳定查询、服务调用以及后续 Agent 接入。

### Business Rule Layer

负责集中管理已经验证的业务规则。

当前规则来源：

```text
src/business_rules.py
```

主要包含：
- RFM Recency 评分规则
- RFM Frequency 评分规则
- RFM Monetary 评分规则
- Customer Segment 分群规则

设计目标：

```text
Business Rules
      |
      +------> Python Analytics
      |
      +------> SQL Views
      |
      +------> Query Service / Agent
```

这样可以避免同一业务规则在多个模块中重复维护，并降低 Python、SQL 和 Agent 结果不一致的风险。

### Tool / Query Service Layer

将分析能力封装为标准化调用接口。

该层负责：
- 加载标准 SQL 查询
- 查询数据库 View
- 参数化业务查询
- 将结构化结果返回给上层 Agent

Agent 不需要重新计算 RFM 或客户分群，只需要查询已经验证的数据视图。

### LLM Layer

负责：
- 语义理解
- 业务问题识别
- 查询结果解释
- 洞察与建议生成

LLM 不负责核心指标计算，避免将确定性计算交给概率模型。

### RAG Layer

提供领域知识增强，例如：
- 数据字典
- Business Rules
- 指标定义
- 项目文档
- 未来行业知识库

### Agent Layer

负责任务规划和工具协调。

Agent 根据用户问题选择合适的数据查询能力，并将结构化结果转换为自然语言业务回答。

## 4. 数据流设计

当前核心数据流：

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

其中，`src/load_database.py` 在完成基础表数据加载后自动执行 `database/views/` 下的 View SQL 文件。

## 5. RFM 数据模型

RFM 模块采用分层 View 设计，减少重复 SQL。

### customer_rfm_base

作用：

计算客户级 RFM 基础指标：

```text
customer_id
recency_days
frequency
monetary
```

解决的问题：

> 每个客户的历史购买行为是什么？

### customer_rfm_scores

输入：

```text
customer_rfm_base
```

作用：

根据已冻结的业务阈值生成：

```text
r_score
f_score
m_score
rfm_code
rfm_score
```

解决的问题：

> 如何将客户的购买行为转换为可比较的客户价值评分？

### customer_segments

输入：

```text
customer_rfm_scores
```

作用：

根据 RFM Score 将客户分类为：
- Champions
- Loyal Customers
- Big Spenders
- High Value Lost
- At Risk
- Lost Customers
- Regular Customers

解决的问题：

> 不同客户应该采取什么业务策略？

## 6. Python 与 SQL 一致性验证

项目通过：

```text
src/check_rfm_consistency.py
```

比较：

```text
Pandas RFM Result
        VS
SQLite View Result
```

验证范围包括：
- Customer count
- Recency
- Frequency
- Monetary
- R Score
- F Score
- M Score
- RFM Score
- Customer Segment

当前验证结果：

```text
RFM reconciliation result:
PASS
```

这保证 Python 分析层与 SQL View 层在核心客户分析逻辑上保持一致。

## 7. Agent 查询执行流

示例问题：

> Loyal Customers 占全部客户多少比例？

执行流：

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

这种设计将复杂业务计算隐藏在稳定的数据模型层中，使 Agent 只负责理解问题和选择查询，而不是重新实现业务逻辑。

## 8. 设计原则

### 计算与推理分离

Python / SQL 负责：
- 数据处理
- 指标计算
- 统计分析
- 业务规则执行

LLM 负责：
- 语义理解
- 业务解释
- 建议生成

### 单一业务规则来源

业务规则集中在：

```text
src/business_rules.py
```

并通过一致性测试保证 SQL View 与 Python 实现同步。

### 分层解耦

系统采用：

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

降低模块之间耦合，便于测试和扩展。

### 可解释性

核心业务指标和客户分类由确定性规则计算，而不是直接交给 LLM 推断。

## 9. 系统扩展能力

架构支持未来集成：
- SQL Query Tools
- Analytics Skills
- Knowledge Retrieval
- Agent Workflow
- Dashboard / BI Layer
- API Service
- Multi-database support
