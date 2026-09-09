# Phase 4 — 高级分析与业务推理

## 1. 阶段目标

Phase 4 的目标是把项目从“确定性查数”进一步升级为“确定性业务推理”，同时保持固定的数据访问链路：

```text
用户
→ LLM / Agent
→ Tool
→ Query Service
→ SQL / View
→ SQLite
```

LLM 不直接查询数据库，也不负责核心业务指标计算。趋势识别、两两比较、差值、差异百分比、完整月份规则以及指标胜者，都由 Python / SQL 确定性计算，再通过 Tool 暴露给 Agent。

Phase 4 有意只聚焦两个高作品集价值能力：

1. Trend Insight
2. Comparison Analytics

本阶段不扩展到预测、异常检测、季节性建模、因果归因或通用 Planner 框架。

## 2. Trend Insight

### 2.1 月度趋势洞察

月度趋势服务返回：

- 销售收入最高月份
- 订单数最高月份
- 收入增长最快月份
- 收入下降最明显月份
- 数据集最新月份
- 数据覆盖起止时间
- 最新月份是否为部分月份

### 2.2 完整月份业务规则

月度排名只使用完整月份。

月度环比比较要求当前月份和前一个月份都完整。

数据集最新月份即使不完整仍然返回，但必须明确标记：

```text
is_partial_month = True
```

这样可以避免把只有部分日期的数据误解为完整自然月的正常下降。

### 2.3 已验证趋势结果

```text
销售收入最高月份：
2011-11
收入：1,509,496.33
订单数：2,769
收入环比：30.69%

订单数最高月份：
2011-11

收入增长最快月份：
2011-05
收入：770,536.02
订单数：1,681
收入环比：43.27%

收入下降最明显月份：
2011-04
收入：537,808.62
订单数：1,246
收入环比：-25.06%

数据集最新月份：
2011-12
收入：638,792.68
订单数：819
收入环比：-57.68%
is_partial_month: True
```

数据覆盖范围：

```text
开始：2010-12-01 08:26:00
结束：2011-12-09 12:50:00
```

## 3. Comparison Analytics

Phase 4 新增确定性的两两比较服务，不再让 LLM 自己扫描原始记录并手工做比较计算。

统一比较方向：

```text
difference = B - A
```

普通数值指标的相对差异：

```text
percentage_difference = (B - A) / A × 100
```

比较结果同时暴露结构化语义字段，例如：

```text
direction
magnitude
magnitude_pct
higher_xxx
```

这样 Agent 可以直接解释比较结果，而不需要重新计算。

## 4. Month Comparison

`month_comparison` 用于比较两个明确指定月份的销售表现。

比较指标：

- revenue
- orders

返回字段包括：

- 有符号差值
- 差异百分比
- 变化方向
- 绝对变化幅度
- 收入更高月份
- 订单更多月份
- 部分月份列表
- 是否可完全比较

已验证示例：

```text
2011-10 vs 2011-11

收入差值：+354,517.03
收入差异百分比：+30.69%

订单差值：+729
订单差异百分比：+35.74%

comparison_is_fully_comparable = True
```

部分月份示例：

```text
2011-11 vs 2011-12

comparison_is_fully_comparable = False
partial_months = ["2011-12"]
```

工具仍然返回当前已观测数值，但 Agent 不应把它解释为两个完整自然月之间的公平比较。

## 5. Product Comparison

`product_comparison` 用于比较两个明确指定 StockCode 的商品。

商品唯一键继续使用：

```text
StockCode = 唯一键
Description = 仅用于展示
```

比较指标：

- revenue
- quantity
- orders

已验证示例：

```text
22423 vs 85123A

收入更高商品：
22423

销量更高商品：
85123A

订单数更多商品：
85123A
```

已验证比较结果：

```text
收入差值：
-68,013.46
-38.98%

销量差值：
+24,073
+173.45%

订单差值：
+277
+13.93%
```

不同指标可以有不同胜者。如果用户没有定义综合评价规则，Agent 应分别说明各指标结果，而不是自行制造唯一整体赢家。

缺失 StockCode 通过：

```text
missing_stock_codes
```

返回，而不是被当成系统故障。

## 6. Customer Segment Comparison

`segment_comparison` 使用现有 RFM 客户分群业务汇总，对两个客户分群进行比较。

比较指标：

- customer_count
- total_revenue
- revenue_percentage
- average_revenue_per_customer

对于 `revenue_percentage`，两个收入占比之间的差异使用：

```text
revenue_percentage_difference_pp
```

即“百分点差”，而不是再把两个百分比做一层相对增长计算。

已验证示例：

```text
Champions vs Loyal Customers

客户数量：
Loyal Customers 更高

总收入：
Champions 更高

收入占比：
Champions 更高

平均每客户收入：
Champions 更高
```

已验证数值：

```text
客户数量差值：
+739
+499.32%

总收入差值：
-626,951.58
-19.48%

收入占比差值：
-7.03 个百分点

平均每客户收入差值：
-18,822.80
-86.57%
```

不同指标胜者不一致时，不自动产生唯一整体赢家。

## 7. Tool Layer

Phase 4 新增工具：

```text
monthly_trend_insights
month_comparison
product_comparison
segment_comparison
```

当前核心 Tool 集合：

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
```

工具调用链保持：

```text
Agent
→ Tool Router
→ Tool
→ Query Service
→ SQL / SQLite
```

Agent 不直接访问数据库。

## 8. Grounding 与可靠性增强

Phase 4 继续保持 Grounding 层轻量、确定性。

当前确定性检查包括：

- Tool 是否执行成功
- 回答是否包含无直接证据的数字
- 回答是否自行补充未经支持的币种 / 货币单位
- Tool Call 参数中的证据
- Tool Result 中的证据

比较服务主动返回结构化语义字段，减少 LLM 重新计算：

- 有符号差值
- 绝对变化幅度
- 差异百分比
- 比较方向
- 更高指标对应实体

Agent 同时增加程序级重复调用抑制：

```text
同一 Tool + 同一参数 + 已成功返回
→ 复用已有结果
→ 不再次执行 Tool
```

这样可以减少不必要的 Tool Round。

为了提高事实型回答稳定性，SiliconFlow Provider 使用：

```text
temperature = 0
```

这会降低回答波动，但不能替代 Grounding Validation。

## 9. Regression 与验收测试

### 9.1 Tool Regression

已验证：

```text
sales_kpi                 PASS
monthly_sales             PASS
monthly_trend_insights    PASS
month_comparison          PASS
customer_value            PASS
product_performance       PASS
product_comparison        PASS
product_concentration     PASS
customer_segments         PASS
segment_comparison        PASS
```

最终结果：

```text
ALL PHASE 4 TOOL REGRESSION TESTS PASSED
```

### 9.2 Agent Regression

完整 Agent 链路已验证：

```text
整体销售概览
→ sales_kpi

最高收入月份
→ monthly_trend_insights

月份比较
→ month_comparison

商品比较
→ product_comparison

客户分群比较
→ segment_comparison
```

测试中的核心回答全部通过 Grounding Validation。

### 9.3 Streamlit Validation

Streamlit AI Analyst 已验证：

- 整体 KPI 分析
- 趋势洞察
- 月份比较
- 商品比较
- 客户分群比较
- Agent Trace 展示
- Grounding Result 展示

Phase 4 核心场景均已通过 UI 端到端测试。

## 10. 已知限制

Phase 4 有意不实现完整语义答案验证。

当前限制包括：

- Grounding Validation 主要验证直接数字和元数据证据，不负责完整语义矛盾检测。
- 回答可能使用了正确数字，但仍可能把“高于 / 低于”等关系描述错误。
- 完整的 comparison direction / semantic contradiction 检查留给后续语义验证层。
- 相对时间表达仍然受限，必要时需要用户澄清。
- 当前分析工具没有暴露币种元数据。
- 因此 Agent 应只展示金额数值，不自行假设货币单位。
- 即使使用低 temperature，LLM 生成仍然具有一定概率性。
- 超大型复合查询可能超过当前 Agent 的最大 Tool Round 配置。
- Streamlit 保存的是 UI 层聊天历史，尚未实现跨问题的完整 Agent 对话记忆。

这些限制会被明确记录，以区分系统的确定性保证与 LLM 的解释能力。

## 11. Phase 4 状态

```text
Phase 4 — 高级分析与业务推理
✅ COMPLETE

Trend Insight
✅ COMPLETE

Month Comparison
✅ COMPLETE

Product Comparison
✅ COMPLETE

Customer Segment Comparison
✅ COMPLETE

Tool Regression
✅ PASS

Agent Regression
✅ PASS

Streamlit Validation
✅ PASS
```

Phase 4 已达到封版条件，可以进入下一阶段。
