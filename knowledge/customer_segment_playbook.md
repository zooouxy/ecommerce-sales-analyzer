# Customer Segment Playbook / 客户分群运营手册

## Metadata / 元数据
```yaml
domain: customer_segmentation
use_for: [segment meaning, segment interpretation, segment recommendations]
do_not_use_for: [exact counts, exact revenue, exact revenue share, exact average revenue per customer]
structured_source_for_facts: customer_segments / segment_comparison
```

# English

## Purpose
This document explains the business meaning of customer segments and suitable operational actions. Exact customer counts, revenue, revenue share, and other numeric facts must come from structured analytical tools.

## Champions
Typical characteristics: recently active, frequent purchasers, high monetary contribution.

Possible actions:
- prioritize retention
- provide loyalty benefits or early access
- encourage advocacy or referrals
- avoid unnecessary broad discounting when loyalty is already strong

## Loyal Customers
Typical characteristics: frequent repeat purchasing, stable relationship, meaningful long-term value.

Possible actions:
- strengthen loyalty programs
- use personalized cross-sell or upsell
- encourage movement toward higher-value engagement
- maintain consistent service quality

## Regular
Typical characteristics: established customers with moderate engagement.

Possible actions:
- encourage repeat purchasing
- improve product discovery
- use targeted recommendations
- identify opportunities to move customers into Loyal Customers

## At Risk
Typical characteristics: previously active or valuable, but engagement is declining.

Possible actions:
- use re-engagement campaigns
- remind customers of relevant products or benefits
- identify friction before using large discounts
- prioritize customers with stronger historical value

## Lost
Typical characteristics: low recent engagement and weak near-term activity without intervention.

Possible actions:
- use low-cost win-back campaigns
- avoid excessive acquisition-like spending
- test responsiveness before increasing incentive cost

## High Value Lost
Typical characteristics: historically high value but currently inactive.

Possible actions:
- prioritize targeted win-back
- use personalized outreach
- investigate likely churn reasons
- use stronger incentives only when justified by historical value

## Big Spenders
Typical characteristics: unusually high monetary contribution and potentially very small sample size.

Possible actions:
- review individually where practical
- protect service quality
- avoid treating a small segment as statistically representative
- monitor concentration risk

## Interpretation Rule
When a user asks both “how much did this segment contribute?” and “what should we do?”, combine:

```text
Structured Tool + RAG knowledge
```

The structured tool provides numeric facts. This playbook provides interpretation and recommendation guidance.

---

# 中文
# 中文

## 用途
本文档用于解释客户分群的业务含义，以及各分群通常适合采取的运营动作。客户数量、收入、收入占比、平均每客户收入等精确数值必须来自结构化分析工具。

## Champions（冠军客户）
典型特征：
- 最近仍然活跃
- 购买频率高
- 收入贡献高

可采取动作：
- 优先客户留存
- 提供会员权益或优先体验
- 鼓励推荐与口碑传播
- 已经具有较强忠诚度时避免不必要的普遍折扣

## Loyal Customers（忠诚客户）
典型特征：
- 复购频繁
- 关系稳定
- 长期收入贡献较为可观

可采取动作：
- 强化会员与忠诚度机制
- 个性化交叉销售或向上销售
- 推动更高价值互动
- 保持稳定服务体验

## Regular（常规客户）
典型特征：
- 已有稳定关系
- 活跃度和收入贡献处于中间水平
- 既不是最高价值，也没有明显流失风险

可采取动作：
- 促进重复购买
- 改善商品发现
- 提供有针对性的推荐
- 寻找向 Loyal Customers 转化的机会

## At Risk（流失风险客户）
典型特征：
- 曾经较活跃或具有一定收入贡献
- 最近参与度正在下降

可采取动作：
- 再激活与召回
- 提醒相关商品或权益
- 大额折扣前先识别流失原因
- 优先处理历史收入贡献更高的客户

## Lost（流失客户）
典型特征：
- 近期活跃度低
- 如果没有干预，短期再次活跃的可能性较弱

可采取动作：
- 使用低成本召回
- 避免投入过高成本
- 增加激励前先测试是否仍有响应

## High Value Lost（高价值流失客户）
典型特征：
- 历史收入贡献较高
- 当前已经明显不活跃

可采取动作：
- 优先定向召回
- 使用个性化触达
- 尝试识别流失原因
- 只有历史价值支持成本时才考虑更强激励

## Big Spenders（高消费客户）
典型特征：
- 收入贡献异常高
- 客户数量可能很少

可采取动作：
- 条件允许时进行个体级分析
- 优先保证服务体验
- 样本较小时不要当作整体代表
- 关注收入集中风险

## 解释规则
客户分群建议属于业务指导，不属于确定性数据事实。

当用户同时询问：

```text
某分群贡献了多少？
以及
应该如何运营该分群？
```

系统应组合：

```text
Structured Tool + RAG knowledge
```

结构化工具提供数值事实；本文档提供解释与建议框架。
