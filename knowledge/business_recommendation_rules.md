# Business Recommendation Rules / 业务建议规则

## Metadata / 元数据
```yaml
domain: business_recommendation
use_for: [recommendation framing, evidence-aware advice, conflicting metrics, fact-vs-recommendation distinction]
do_not_use_for: [exact business metrics, unsupported causal conclusions]
structured_source_for_facts: analytical tools
```

# English

## Purpose
This document defines how the AI Analyst should convert analytical evidence into cautious business recommendations. Recommendations are not deterministic facts.

## Rule 1 — Facts Before Advice
Recommendations should follow evidence.

Preferred structure:
```text
Observed fact
→ interpretation
→ possible action
```

Do not invent an action first and search for justification afterward.

## Rule 2 — Separate Fact, Interpretation, and Recommendation
A good response distinguishes:
- Fact: directly supported by structured data or retrieved knowledge
- Interpretation: what the fact may indicate
- Recommendation: a possible business action

Avoid expressing interpretation or recommendation as if it were measured fact.

## Rule 3 — Do Not Invent Causes
A change in revenue or customer behavior does not establish its cause.

Do not claim that a result was caused by marketing, price, promotion, seasonality, competition, or inventory unless supporting evidence exists.

## Rule 4 — Handle Conflicting Metrics Explicitly
When metrics disagree:
- describe each metric separately
- avoid forcing one overall winner
- ask for an evaluation standard if a single decision is required

Example:
```text
Product A has higher revenue.
Product B has higher quantity and order count.
No unique overall winner is defined without a weighting rule.
```

## Rule 5 — Respect Data Completeness
Do not make strong period comparisons when the comparison is not fully comparable.

Partial-period data can support observations, but not normal full-period conclusions.

## Rule 6 — Avoid Unsupported Precision
Do not generate new ratios, multipliers, percentage transformations, or rankings unless they are returned by a tool or explicitly requested and safely computed.

## Rule 7 — Use RAG for Knowledge, Not Numeric Truth
Use RAG for:
- definitions
- interpretation frameworks
- general operational strategies
- analysis playbooks

Use structured tools for:
- revenue
- orders
- quantity
- customer counts
- percentages
- rankings
- comparisons

## Rule 8 — Evidence Insufficient Means Say So
When evidence is insufficient, state the limitation. Do not turn uncertainty into a confident business claim.

---

# 中文

## 用途
本文档规定 AI Analyst 如何把分析证据转化为谨慎、可解释的业务建议。业务建议不是确定性事实。

## 规则 1 — 先有事实，再有建议
建议应建立在证据之后。

推荐结构：
```text
观测事实
→ 解释
→ 可选行动
```

不要先生成行动方案，再倒推证据。

## 规则 2 — 区分事实、解释和建议
好的回答应区分：
- 事实：直接由结构化数据或检索知识支持
- 解释：该事实可能意味着什么
- 建议：可以考虑采取什么业务动作

不能把解释或建议写成已经被数据测量证明的事实。

## 规则 3 — 不自行生成因果结论
收入或客户行为发生变化，并不能自动证明原因。

没有证据时，不应声称变化由营销、价格、促销、季节性、竞争或库存导致。

## 规则 4 — 显式处理指标冲突
多个指标结果不一致时：
- 分别说明每个指标
- 不强行定义唯一整体赢家
- 如果业务决策必须选一个，应要求评价标准或权重

例如：
```text
商品 A 收入更高。
商品 B 销量和订单数更高。
如果没有权重规则，则不存在唯一整体赢家。
```

## 规则 5 — 尊重数据完整性
当两个周期不具备完全可比性时，不做强结论。

部分周期数据可以支持“当前观测”，但不能支持正常完整周期结论。

## 规则 6 — 避免无证据精确计算
不要自行生成新比例、倍数、百分比转换或排名，除非这些结果由 Tool 返回，或用户明确要求且能够安全计算。

## 规则 7 — RAG 提供知识，不提供数值真相
RAG 适合提供：
- 定义
- 解释框架
- 通用运营策略
- 分析 playbook

结构化工具负责：
- 收入
- 订单
- 销量
- 客户数量
- 百分比
- 排名
- 比较结果

## 规则 8 — 证据不足就明确说明
当证据不足时，应明确表达限制。不能把不确定性包装成确定业务结论。
