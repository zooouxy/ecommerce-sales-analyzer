# E-commerce Sales Analyzer

> AI-powered ecommerce analytics project combining deterministic data analysis, SQL-based analytical serving, an LLM agent, local RAG business knowledge, provenance-aware hybrid reasoning, and an interactive Streamlit dashboard.

---

# English

## Project Introduction

E-commerce Sales Analyzer is an AI-powered ecommerce analytics project that combines structured data analysis, deterministic business logic, SQL-based analytical serving, an LLM agent, local RAG business knowledge, provenance-aware hybrid reasoning, and an interactive Streamlit dashboard.

The project follows a layered architecture:

```text
User
→ Streamlit / AI Analyst
→ Agent Tool Layer
→ Query Service
→ SQL / Analytical Views
→ SQLite
```

Business calculations remain deterministic in Pandas, Python, and SQL. The LLM is responsible for understanding user intent, selecting analytical tools, and interpreting structured results.

A core design principle is:

> The LLM does not query the database directly.

All analytical requests are routed through the Tool Layer and Query Service before reaching SQL / SQLite.

---

## Project Progress

### Phase 1 — Data Analytics & Query Layer
✅ Complete

- Data cleaning and preprocessing
- Pandas-based business analysis
- Stable business rules
- SQLite analytical models and views
- Query Service abstraction
- Sales analytics
- Product analytics
- Customer value analytics
- RFM customer segmentation
- Pandas / SQL consistency validation

### Phase 2 — LLM Agent Integration & Fact-Grounded Tool Orchestration
✅ Complete

- LLM provider abstraction
- SiliconFlow integration
- Qwen/Qwen3-8B
- OpenAI-compatible API integration
- Tool Calling
- Multi-round Agent loop
- Tool Registry
- Tool Router
- Query Service integration
- Core ecommerce analysis tools
- Intent routing
- Parameter extraction
- Grounding validation
- Empty-result handling
- Multi-tool orchestration
- Duplicate Tool Call control
- Deterministic edge-case tests
- Phase 2 acceptance testing
- Known limitations documentation

### Phase 3 — Streamlit AI Ecommerce Dashboard & Interactive Analytics
✅ Complete

- Executive KPI dashboard
- Monthly revenue trend analysis
- Monthly sales detail table
- Product revenue concentration metrics
- Top 10 product performance analysis
- Product lookup by StockCode
- Customer segment overview
- Customer segment revenue analysis
- Customer lookup by Customer ID
- AI Analyst natural-language chat interface
- Agent Tool Call trace
- Tool Result visibility
- Grounding validation visibility
- Streamlit session-based chat history
- User-facing error handling
- Phase 3 smoke testing

### Phase 4 — Advanced Analytics & Business Reasoning
✅ Complete

- Monthly Trend Insight
- Complete-month ranking rules
- Partial-month detection
- Month-to-month comparison
- Product-to-product comparison
- Customer-segment comparison
- Deterministic difference semantics
- Metric-level winner fields
- Duplicate successful Tool Call suppression
- Lower-variance LLM generation with `temperature=0`
- Tool regression testing
- Agent regression testing
- Streamlit end-to-end validation

Detailed documentation:

```text
docs/en/Phase4_Advanced_Analytics_EN.md
docs/zh/Phase4_Advanced_Analytics_CN.md
```

### Phase 5 — Structured Data + RAG Hybrid
✅ Complete

- Five-document bilingual ecommerce knowledge base
- Markdown heading-aware knowledge loading and chunking
- SiliconFlow embedding integration with `Qwen/Qwen3-Embedding-0.6B`
- Local NumPy cosine-similarity vector store
- JSON index persistence in `data/rag_index.json`
- Language-aware retrieval and bilingual duplicate suppression
- `business_knowledge_search` Tool integration
- Structured-only / RAG-only / Hybrid routing
- Deterministic customer-segment knowledge claims, selection, and rendering
- `deterministic_rag` answer mode
- `deterministic_hybrid` answer mode
- Explicit provenance for model general knowledge
- Deterministic unsupported-number / unsupported-currency sanitizer
- RAG source alignment in Grounding trace
- Phase 5 Agent regression testing
- Streamlit Answer Mode and Knowledge Sources visibility

Detailed documentation:

```text
docs/en/Phase5_Structured_Data_RAG_Hybrid_EN.md
docs/zh/Phase5_Structured_Data_RAG_Hybrid_CN.md
```

### Phase 6 — Portfolio Packaging & Demo
⬜ Planned

Planned focus:

- Final documentation
- Architecture diagram
- Screenshots and demo workflow
- GitHub cleanup
- Portfolio-ready presentation and demo

---

## Current Analytics Capabilities

### Sales Analytics

- Overall revenue
- Total orders
- Total quantity
- Average order value
- Monthly revenue
- Monthly order volume
- Monthly revenue growth
- Highest-revenue month
- Highest-order month
- Largest monthly revenue growth
- Largest monthly revenue decline
- Latest-month completeness detection

### Product Analytics

- Product revenue
- Product quantity
- Product order count
- Product ranking
- Top 10 product revenue
- Top 10 revenue concentration
- Pairwise product comparison by StockCode
- Revenue / quantity / order comparison semantics
- Metric-level product winners

### Customer Analytics

- Customer order count
- Customer revenue
- Customer average order value
- First purchase date
- Last purchase date
- RFM customer segmentation
- Segment-level customer count
- Segment revenue contribution
- Average revenue per customer
- Pairwise customer-segment comparison
- Revenue-share comparison in percentage points

### Comparison Analytics

All pairwise comparison services use the same directional convention:

```text
difference = B - A
```

For ordinary numeric metrics:

```text
percentage_difference = (B - A) / A × 100
```

If the baseline `A` equals zero, the percentage difference is returned as `None`.

The comparison layer exposes structured fields such as:

```text
direction
magnitude
magnitude_pct
higher_xxx
```

This reduces the need for the LLM to recompute deterministic facts.

---

## Monthly Completeness Rule

Monthly trend ranking uses complete months only.

Month-over-month comparison requires both the current month and the previous month to be complete.

The latest dataset month is still returned even when incomplete, but it is explicitly marked as a partial month.

Current data coverage:

```text
2010-12-01 08:26:00
→
2011-12-09 12:50:00
```

Therefore:

```text
2011-12
is_partial_month = True
```

A partial month can still be queried, but it must not be interpreted as fully comparable to a complete month.

---

## Current Agent Tools

The current core Tool Layer includes:

```text
sales_kpi
monthly_sales
monthly_trend_insights
month_comparison
customer_value
product_performance
product_comparison
product_concentration
customer_segments
segment_comparison
business_knowledge_search
```

The frozen Agent access path remains:

```text
User
→ LLM / Agent
→ Tool
→ Query Service
→ SQL / View
→ SQLite
```

The Agent never queries SQLite directly.

---

## AI Analyst

The AI Analyst allows users to ask ecommerce business questions in natural language.

Example questions:

```text
2011年11月销售情况怎么样？

哪个月销售收入最高？

2011-10和2011-11哪个月收入更高？

商品22423和85123A哪个收入更高？

Champions和Loyal Customers哪个收入贡献更高？

商品22423的销售表现怎么样？

Champions客户贡献了多少收入？

整体销售收入是多少，同时Top 10商品占整体商品收入多少？
```

The Agent selects between structured analytical tools and business-knowledge retrieval. Structured facts continue to come from the Query Service, while explanatory and operational knowledge can come from RAG.

Phase 5 supports:

```text
Structured-only
RAG-only
Hybrid
General model suggestions with explicit provenance
```

The Streamlit interface exposes:

```text
Answer Mode
Tool Calls
Tool Results
Grounding Validation
Knowledge Sources
```

This makes the Agent workflow observable rather than operating as a black box.

---

## Trend Insight

The `monthly_trend_insights` capability provides deterministic trend summaries.

Verified results include:

```text
Highest revenue month:
2011-11
Revenue: 1,509,496.33
Orders: 2,769
Revenue growth: 30.69%

Largest revenue growth:
2011-05
Revenue growth: 43.27%

Largest revenue decline:
2011-04
Revenue growth: -25.06%

Latest month:
2011-12
Revenue: 638,792.68
Orders: 819
Revenue growth: -57.68%
is_partial_month: True
```

The latest-month result remains queryable while being explicitly marked as incomplete.

---

## Comparison Intelligence

### Month Comparison

`month_comparison` compares two explicit months across:

```text
revenue
orders
```

It also returns:

```text
difference
percentage_difference
direction
magnitude
higher_xxx
partial_months
comparison_is_fully_comparable
```

Example:

```text
2011-10 → 2011-11

Revenue difference: +354,517.03
Revenue difference pct: +30.69%

Orders difference: +729
Orders difference pct: +35.74%
```

### Product Comparison

`product_comparison` compares two StockCodes across:

```text
revenue
quantity
orders
```

Example:

```text
22423 vs 85123A

Higher revenue:
22423

Higher quantity:
85123A

Higher orders:
85123A
```

StockCode is the unique product key. Description is display-only metadata.

### Customer Segment Comparison

`segment_comparison` compares two customer segments across:

```text
customer_count
total_revenue
revenue_percentage
average_revenue_per_customer
```

Revenue share differences are represented in percentage points:

```text
revenue_percentage_difference_pp
```

rather than as relative growth between percentages.

If multiple metrics have different winners, the Agent reports metric-level results. It does not invent one overall winner unless the user provides an evaluation rule or weighting standard.

---

## Structured Data + RAG Hybrid

Phase 5 introduces a second evidence path without changing the structured-data contract:

```text
User
│
└── AI Analyst
    └── LLM Agent
        ├── Structured Tools
        │   └── Query Service
        │       └── SQL / Views
        │           └── SQLite
        │
        └── business_knowledge_search
            └── Knowledge Retriever
                └── Local Vector Store
                    └── Bilingual Knowledge Base
```

Supported response paths:

```text
Structured-only
RAG-only
Hybrid
General Suggestions with explicit provenance
```

For supported customer-segmentation knowledge, RAG output uses deterministic claims, selection, and rendering. Hybrid customer-segment answers deterministically combine structured facts with rendered knowledge instead of asking the LLM to rewrite both sources.

## Grounding & Reliability

The Grounding layer intentionally remains lightweight and deterministic.

Current checks include:

- Tool execution success
- Unsupported numeric claims
- Unsupported currency or monetary units
- Numeric evidence from Tool Call arguments
- Numeric and metadata evidence from Tool Results
- RAG Tool usage and evidence availability
- Retrieved knowledge source tracking
- Selected-source alignment for deterministic knowledge output
- Deterministic sanitation of unsupported numeric / currency claims in free-form answers

The Agent also includes duplicate successful Tool Call suppression:

```text
same tool
+ same arguments
+ previous successful result
→ reuse cached result
→ do not execute again
```

This prevents redundant calls from consuming unnecessary Agent rounds.

For more stable factual generation, the SiliconFlow provider uses:

```text
temperature = 0
```

This reduces output variability but does not replace Grounding Validation.

---

## System Architecture

```text
User
│
├── Streamlit Dashboard
│   └── Query Service
│       └── SQL / Analytical Views
│           └── SQLite
│
└── AI Analyst
    └── LLM Agent
        └── Tool Layer
            └── Query Service
                └── SQL / Analytical Views
                    └── SQLite
```

The frozen Agent access path is:

```text
User
→ LLM / Agent
→ Tool
→ Query Service
→ SQL / View
→ SQLite
```

Business computation stays deterministic. The LLM handles intent understanding, tool selection, and interpretation.

---

## LLM Provider

Current provider:

```text
SiliconFlow
Model: Qwen/Qwen3-8B
```

The project uses an LLM provider abstraction so the provider can be replaced without changing the core Agent architecture.

The current factual-generation configuration uses:

```text
temperature = 0
```

to reduce unnecessary response variance.

---

## Testing

### Phase 4 Tool Regression

Current regression coverage verifies:

```text
sales_kpi
monthly_sales
monthly_trend_insights
month_comparison
customer_value
product_performance
product_comparison
product_concentration
customer_segments
segment_comparison
business_knowledge_search
```

Verified result:

```text
ALL PHASE 4 TOOL REGRESSION TESTS PASSED
```

### Phase 4 Agent Regression

Validated routes include:

```text
Overall sales
→ sales_kpi

Highest revenue month
→ monthly_trend_insights

Month comparison
→ month_comparison

Product comparison
→ product_comparison

Customer-segment comparison
→ segment_comparison
business_knowledge_search
```

Verified result:

```text
ALL PHASE 4 AGENT REGRESSION TESTS PASSED
```

### Phase 5 Agent Regression

Validated routes include:

```text
Structured-only
→ customer_segments

RAG-only
→ business_knowledge_search
→ deterministic_rag

Hybrid
→ customer_segments + business_knowledge_search
→ deterministic_hybrid

General Suggestions
→ explicit non-knowledge-base provenance

Phase 4 Product Comparison
→ product_comparison
```

Verified result:

```text
ALL PHASE 5 AGENT REGRESSION TESTS PASSED
```

### Streamlit Validation

The following AI Analyst scenarios were validated successfully in the UI:

```text
Overall sales overview
Monthly trend insight
Month comparison
Product comparison
Customer segment comparison
RAG-only customer-segment strategy
Structured + RAG Hybrid
General Suggestions provenance
```

Tool Calls, Tool Results, and Grounding Validation were also verified through the Streamlit interface.

---

## Running the Project

### 1. Create and activate the virtual environment

Windows Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```text
SILICONFLOW_API_KEY=your_api_key
SILICONFLOW_MODEL=Qwen/Qwen3-8B
SILICONFLOW_EMBEDDING_MODEL=Qwen/Qwen3-Embedding-0.6B
```

Do not commit `.env` to Git.

### 4. Run the Streamlit app

```bash
python -m streamlit run app.py
```

The application will normally be available at:

```text
http://localhost:8501
```

### 5. Run regression tests

Phase 4:

```bash
PYTHONIOENCODING=utf-8 python tests/test_phase4_regression.py
```

```bash
PYTHONIOENCODING=utf-8 python tests/test_agent_regression.py
```

Phase 5:

```bash
PYTHONIOENCODING=utf-8 python tests/test_phase5_regression.py
```

---

## Core Dependencies

```text
numpy==2.0.2
pandas==2.3.3
openpyxl==3.1.5

matplotlib==3.9.4
seaborn==0.13.2
jupyter==1.1.1

streamlit==1.50.0
openai==2.48.0
python-dotenv==1.2.1
```

---

## Known Limitations

The system intentionally separates deterministic guarantees from LLM interpretation.

Known limitations include:

- Relative-time expressions may require clarification
- Grounding Validation checks direct evidence but does not perform full semantic contradiction detection
- A response may use supported numbers while still describing a higher/lower relationship incorrectly
- Full comparison-direction and contradiction validation is deferred to a later semantic validation layer
- Currency metadata is not currently exposed by analytical tools
- Monetary values should therefore be displayed without inventing a currency
- LLM Tool Calling and natural-language generation remain probabilistic
- `temperature=0` reduces variance but does not make generation mathematically deterministic
- Streamlit chat history is UI-level history; the Agent does not yet maintain full cross-question conversational memory
- Very large compound requests may exceed the configured maximum number of Agent tool rounds
- The current Grounding layer intentionally remains lightweight instead of becoming a second reasoning model
- Deterministic knowledge-claim extraction is currently strongest for customer-segmentation knowledge
- Other RAG domains can still rely on retrieved chunks plus LLM synthesis
- The local knowledge base is manually maintained
- The current RAG stack intentionally excludes rerankers, BM25, query rewriting, external vector databases, and a second LLM judge
- Explicitly requested model-general suggestions are allowed but are labeled separately from knowledge-base content

See:

```text
docs/en/Phase4_Advanced_Analytics_EN.md
docs/zh/Phase4_Advanced_Analytics_CN.md
```

for Phase 4 implementation details and limitations.

---

## Project Status

```text
Phase 1 — Data Analytics & Query Layer
✅ Complete

Phase 2 — LLM Agent Integration & Fact-Grounded Tool Orchestration
✅ Complete

Phase 3 — Streamlit AI Ecommerce Dashboard & Interactive Analytics
✅ Complete

Phase 4 — Advanced Analytics & Business Reasoning
✅ Complete

Phase 5 — Structured Data + RAG Hybrid
✅ Complete

Phase 6 — Portfolio Packaging & Demo
⬜ Planned
```

---

# 中文

## 项目简介

E-commerce Sales Analyzer 是一个 AI 驱动的电商数据分析项目，将结构化数据分析、确定性业务计算、SQL 分析服务层、LLM 智能体、本地 RAG 业务知识、来源可追踪的混合推理以及 Streamlit 交互式仪表盘整合在同一个系统中。

项目采用分层架构：

```text
用户
→ Streamlit / AI Analyst
→ Agent Tool Layer
→ Query Service
→ SQL / Analytical Views
→ SQLite
```

业务指标与核心计算由 Pandas、Python 和 SQL 确定性完成；LLM 主要负责理解用户意图、选择分析工具，并基于结构化结果进行解释和回答。

项目的一项核心设计原则是：

> LLM 不直接查询数据库。

所有分析请求都必须先经过 Tool Layer 和 Query Service，再访问 SQL / SQLite。

---

## 项目进度

### Phase 1 — 数据分析与查询层
✅ 已完成

- 数据清洗与预处理
- 基于 Pandas 的业务分析
- 稳定业务规则
- SQLite 分析模型与视图
- Query Service 抽象层
- 销售分析
- 商品分析
- 客户价值分析
- RFM 客户分群
- Pandas / SQL 一致性验证

### Phase 2 — LLM 智能体集成与基于事实的工具调度
✅ 已完成

- LLM Provider 抽象层
- SiliconFlow 集成
- Qwen/Qwen3-8B
- OpenAI-compatible API 集成
- Tool Calling
- 多轮 Agent 执行循环
- Tool Registry
- Tool Router
- Query Service 集成
- 核心电商分析工具
- 意图路由
- 参数提取
- Grounding 验证
- 空结果处理
- 多工具调度
- 重复 Tool Call 控制
- 确定性边界测试
- Phase 2 Acceptance Test
- Known Limitations 文档

### Phase 3 — Streamlit AI 电商分析仪表盘与交互分析
✅ 已完成

- Executive KPI 仪表盘
- 月度收入趋势分析
- 月度销售明细表
- 商品收入集中度指标
- Top 10 商品表现分析
- 按 StockCode 查询商品
- 客户分群概览
- 客户分群收入分析
- 按 Customer ID 查询客户
- AI Analyst 自然语言聊天界面
- Agent Tool Call 执行轨迹
- Tool Result 可视化
- Grounding Validation 可视化
- 基于 Streamlit Session State 的聊天记录
- 面向用户的错误处理
- Phase 3 Smoke Test

### Phase 4 — 高级分析与业务推理
✅ 已完成

- 月度趋势洞察
- 完整月份排名规则
- 部分月份识别
- 月份两两比较
- 商品两两比较
- 客户分群两两比较
- 确定性差异语义
- 指标级胜者字段
- 成功 Tool Call 重复调用抑制
- `temperature=0` 降低事实型输出波动
- Tool Regression
- Agent Regression
- Streamlit 端到端验收

详细文档：

```text
docs/en/Phase4_Advanced_Analytics_EN.md
docs/zh/Phase4_Advanced_Analytics_CN.md
```

### Phase 5 — Structured Data + RAG Hybrid
✅ 已完成

- 5 个中英双语电商业务知识文档
- 基于 Markdown Heading 的知识加载与 Chunking
- SiliconFlow Embedding：`Qwen/Qwen3-Embedding-0.6B`
- NumPy Cosine Similarity 本地向量检索
- `data/rag_index.json` JSON 索引持久化
- 语言偏好与中英重复内容抑制
- `business_knowledge_search` Tool 集成
- Structured-only / RAG-only / Hybrid 路由
- 客户分群知识的确定性 Claim / Selector / Renderer
- `deterministic_rag` Answer Mode
- `deterministic_hybrid` Answer Mode
- 模型通用知识显式 Provenance 分层
- Unsupported Number / Currency 确定性 Sanitizer
- Grounding Trace 中的 RAG Source Alignment
- Phase 5 Agent Regression
- Streamlit Answer Mode 与 Knowledge Sources 展示

详细文档：

```text
docs/en/Phase5_Structured_Data_RAG_Hybrid_EN.md
docs/zh/Phase5_Structured_Data_RAG_Hybrid_CN.md
```

### Phase 6 — 作品集包装与 Demo
⬜ 计划中

计划重点：

- 最终项目文档
- 架构图
- 截图与 Demo 流程
- GitHub 清理
- 作品集展示材料与演示

---

## 当前分析能力

### 销售分析

- 整体销售收入
- 总订单数
- 总销售数量
- 平均订单价值
- 月度销售收入
- 月度订单量
- 月度收入增长率
- 收入最高月份
- 订单数最高月份
- 月度收入最大增长
- 月度收入最大下降
- 最新月份完整性识别

### 商品分析

- 商品收入
- 商品销量
- 商品订单数
- 商品排名
- Top 10 商品收入
- Top 10 商品收入集中度
- 基于 StockCode 的商品两两比较
- 收入 / 销量 / 订单数比较语义
- 指标级商品胜者

### 客户分析

- 客户订单数
- 客户总收入贡献
- 客户平均订单价值
- 首次购买日期
- 最近购买日期
- RFM 客户分群
- 分群客户数量
- 分群收入贡献
- 客户平均收入贡献
- 客户分群两两比较
- 收入占比百分点差异

### 比较分析

所有两两比较服务统一使用：

```text
difference = B - A
```

普通数值指标的差异百分比：

```text
percentage_difference = (B - A) / A × 100
```

当基准值 `A = 0` 时，差异百分比返回 `None`。

比较层同时提供：

```text
direction
magnitude
magnitude_pct
higher_xxx
```

等结构化字段，减少 LLM 自行重新计算确定性事实。

---

## 月份完整性规则

月度趋势排名只使用完整月份。

月度环比比较要求当前月份和前一个月份都完整。

数据集最新月份即使不完整仍然返回，但必须明确标记为部分月份。

当前数据覆盖范围：

```text
2010-12-01 08:26:00
→
2011-12-09 12:50:00
```

因此：

```text
2011-12
is_partial_month = True
```

部分月份仍然可以查询，但不能被解释为与完整月份完全可比。

---

## 当前 Agent Tools

当前核心 Tool Layer 包括：

```text
sales_kpi
monthly_sales
monthly_trend_insights
month_comparison
customer_value
product_performance
product_comparison
product_concentration
customer_segments
segment_comparison
business_knowledge_search
```

Agent 的固定数据访问链路保持：

```text
用户
→ LLM / Agent
→ Tool
→ Query Service
→ SQL / View
→ SQLite
```

Agent 不直接查询 SQLite。

---

## AI Analyst

AI Analyst 支持用户使用自然语言提出电商业务问题。

示例问题：

```text
2011年11月销售情况怎么样？

哪个月销售收入最高？

2011-10和2011-11哪个月收入更高？

商品22423和85123A哪个收入更高？

Champions和Loyal Customers哪个收入贡献更高？

商品22423的销售表现怎么样？

Champions客户贡献了多少收入？

整体销售收入是多少，同时Top 10商品占整体商品收入多少？
```

Agent 会根据问题在结构化分析 Tool 与业务知识检索之间进行路由。确定性数据事实继续来自 Query Service，而业务定义、解释框架与运营知识可以来自 RAG。

Phase 5 支持：

```text
Structured-only
RAG-only
Hybrid
显式标注来源的模型通用建议
```

Streamlit 页面同时展示：

```text
Answer Mode
Tool Calls
Tool Results
Grounding Validation
Knowledge Sources
```

因此 Agent 的执行过程是可观察的，而不是完全黑盒。

---

## Trend Insight

`monthly_trend_insights` 提供确定性的月度趋势摘要。

已验证结果：

```text
销售收入最高月份：
2011-11
收入：1,509,496.33
订单数：2,769
收入环比：30.69%

收入增长最快月份：
2011-05
收入环比：43.27%

收入下降最明显月份：
2011-04
收入环比：-25.06%

数据集最新月份：
2011-12
收入：638,792.68
订单数：819
收入环比：-57.68%
is_partial_month: True
```

最新月份虽然可查询，但会明确标记为不完整月份。

---

## Comparison Intelligence

### 月份比较

`month_comparison` 比较两个明确月份的：

```text
revenue
orders
```

并返回：

```text
difference
percentage_difference
direction
magnitude
higher_xxx
partial_months
comparison_is_fully_comparable
```

示例：

```text
2011-10 → 2011-11

收入差值：+354,517.03
收入差异百分比：+30.69%

订单差值：+729
订单差异百分比：+35.74%
```

### 商品比较

`product_comparison` 比较两个 StockCode 的：

```text
revenue
quantity
orders
```

示例：

```text
22423 vs 85123A

收入更高：
22423

销量更高：
85123A

订单数更多：
85123A
```

StockCode 是商品唯一键，Description 只作为展示字段。

### 客户分群比较

`segment_comparison` 比较两个客户分群的：

```text
customer_count
total_revenue
revenue_percentage
average_revenue_per_customer
```

收入占比差异使用百分点：

```text
revenue_percentage_difference_pp
```

而不是对两个百分比再计算相对增长率。

当多个指标的胜者不同，如果用户没有提供综合评价标准或权重，Agent 不自行定义唯一整体赢家。

---

## Structured Data + RAG Hybrid

Phase 5 在不改变结构化数据访问契约的前提下增加第二条知识证据路径：

```text
用户
│
└── AI Analyst
    └── LLM Agent
        ├── Structured Tools
        │   └── Query Service
        │       └── SQL / Views
        │           └── SQLite
        │
        └── business_knowledge_search
            └── Knowledge Retriever
                └── Local Vector Store
                    └── Bilingual Knowledge Base
```

当前支持：

```text
Structured-only
RAG-only
Hybrid
显式 Provenance 的 General Suggestions
```

对于支持的客户分群知识，RAG 使用确定性 Claim、Selector 和 Renderer。客户分群 Hybrid 回答会确定性组合结构化事实与知识库文本，而不是再次让 LLM 自由改写两类证据。

## Grounding 与可靠性

Grounding 层有意保持轻量、确定性。

当前检查包括：

- Tool 执行是否成功
- 回答是否包含无直接证据的数字
- 回答是否自行补充未经支持的币种 / 货币单位
- Tool Call 参数中的数字证据
- Tool Result 中的数字和元数据证据
- RAG Tool 调用与证据可用性
- 检索知识来源追踪
- 确定性知识输出的 Selected Source Alignment
- 自由生成回答中 Unsupported Number / Currency 的确定性清理

Agent 还实现了成功 Tool Call 的程序级去重：

```text
同一 Tool
+ 同一参数
+ 已存在成功结果
→ 复用已有结果
→ 不重复执行
```

这样可以避免重复调用浪费 Agent Tool Round。

为了提高事实型回答稳定性，SiliconFlow Provider 当前使用：

```text
temperature = 0
```

这会降低输出波动，但不能替代 Grounding Validation。

---

## 系统架构

```text
用户
│
├── Streamlit Dashboard
│   └── Query Service
│       └── SQL / Analytical Views
│           └── SQLite
│
└── AI Analyst
    └── LLM Agent
        └── Tool Layer
            └── Query Service
                └── SQL / Analytical Views
                    └── SQLite
```

Agent 的固定数据访问链路为：

```text
用户
→ LLM / Agent
→ Tool
→ Query Service
→ SQL / View
→ SQLite
```

业务计算保持确定性；LLM 负责意图理解、工具选择和结果解释。

---

## LLM Provider

当前 Provider：

```text
SiliconFlow
Model: Qwen/Qwen3-8B
```

项目通过 LLM Provider 抽象层隔离模型供应商，因此未来可以替换模型或 Provider，而无需修改核心 Agent 架构。

当前事实型生成配置使用：

```text
temperature = 0
```

用于减少不必要的回答波动。

---

## 测试

### Phase 4 Tool Regression

当前回归覆盖：

```text
sales_kpi
monthly_sales
monthly_trend_insights
month_comparison
customer_value
product_performance
product_comparison
product_concentration
customer_segments
segment_comparison
business_knowledge_search
```

验证结果：

```text
ALL PHASE 4 TOOL REGRESSION TESTS PASSED
```

### Phase 4 Agent Regression

已验证路由：

```text
整体销售
→ sales_kpi

最高收入月份
→ monthly_trend_insights

月份比较
→ month_comparison

商品比较
→ product_comparison

客户分群比较
→ segment_comparison
business_knowledge_search
```

验证结果：

```text
ALL PHASE 4 AGENT REGRESSION TESTS PASSED
```

### Phase 5 Agent Regression

已验证路由：

```text
Structured-only
→ customer_segments

RAG-only
→ business_knowledge_search
→ deterministic_rag

Hybrid
→ customer_segments + business_knowledge_search
→ deterministic_hybrid

General Suggestions
→ 显式标注非知识库来源

Phase 4 商品比较回归
→ product_comparison
```

验证结果：

```text
ALL PHASE 5 AGENT REGRESSION TESTS PASSED
```

### Streamlit Validation

以下 AI Analyst 场景均已通过 UI 验收：

```text
整体销售概览
月度趋势洞察
月份比较
商品比较
客户分群比较
RAG-only 客户分群策略
Structured + RAG Hybrid
General Suggestions Provenance
```

同时验证了：

```text
Tool Calls
Tool Results
Grounding Validation
```

在 Streamlit 页面中的展示与执行。

---

## 项目运行方式

### 1. 创建并激活虚拟环境

Windows Git Bash：

```bash
python -m venv .venv
source .venv/Scripts/activate
```

### 2. 安装依赖

```bash
python -m pip install -r requirements.txt
```

### 3. 配置环境变量

在项目根目录创建 `.env`：

```text
SILICONFLOW_API_KEY=your_api_key
SILICONFLOW_MODEL=Qwen/Qwen3-8B
SILICONFLOW_EMBEDDING_MODEL=Qwen/Qwen3-Embedding-0.6B
```

不要将 `.env` 提交到 Git。

### 4. 启动 Streamlit

```bash
python -m streamlit run app.py
```

通常可以通过以下地址访问：

```text
http://localhost:8501
```

### 5. 运行回归测试

Phase 4：

```bash
PYTHONIOENCODING=utf-8 python tests/test_phase4_regression.py
```

```bash
PYTHONIOENCODING=utf-8 python tests/test_agent_regression.py
```

Phase 5：

```bash
PYTHONIOENCODING=utf-8 python tests/test_phase5_regression.py
```

---

## 核心依赖

```text
numpy==2.0.2
pandas==2.3.3
openpyxl==3.1.5

matplotlib==3.9.4
seaborn==0.13.2
jupyter==1.1.1

streamlit==1.50.0
openai==2.48.0
python-dotenv==1.2.1
```

---

## 已知限制

当前系统有意区分“确定性保证”和“LLM 解释能力”。

已知限制包括：

- 相对时间表达可能需要用户补充说明
- Grounding Validation 验证直接证据，但不负责完整语义矛盾检测
- 回答可能使用了有证据支持的数字，却仍然把“高于 / 低于”等关系描述错误
- 完整的 comparison direction / semantic contradiction 验证留给后续语义验证层
- 当前分析工具没有暴露币种元数据
- 因此金额应只显示数值，不自行假设货币单位
- LLM Tool Calling 和自然语言生成仍然具有概率性
- `temperature=0` 会降低波动，但不代表数学意义上的完全确定
- Streamlit 当前保存的是 UI 层聊天历史，Agent 尚未维护跨问题的完整对话记忆
- 超大型复合查询可能超过当前 Agent 配置的最大 Tool Calling 轮数
- 当前 Grounding 层有意保持轻量，不把它扩展成第二个推理模型
- 确定性 Knowledge Claim 抽取目前主要覆盖客户分群知识
- 其他 RAG 知识域仍可能使用检索 Chunk + LLM 生成
- 当前知识库由本地文件人工维护
- 当前 RAG 栈有意不加入 reranker、BM25、query rewriting、外部向量数据库或第二个 LLM Judge
- 用户明确请求的模型通用建议可以生成，但必须与知识库内容显式区分

Phase 4 的详细实现与限制请参考：

```text
docs/en/Phase4_Advanced_Analytics_EN.md
docs/zh/Phase4_Advanced_Analytics_CN.md
```

---

## 项目状态

```text
Phase 1 — 数据分析与查询层
✅ 已完成

Phase 2 — LLM 智能体集成与基于事实的工具调度
✅ 已完成

Phase 3 — Streamlit AI 电商分析仪表盘与交互分析
✅ 已完成

Phase 4 — 高级分析与业务推理
✅ 已完成

Phase 5 — Structured Data + RAG Hybrid
✅ 已完成

Phase 6 — 作品集包装与 Demo
⬜ 计划中
```
