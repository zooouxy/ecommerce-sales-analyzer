# Business Rules（业务规则冻结版）

版本：v1.0\
状态：已验证并冻结（Frozen）

## 1. 数据范围定义

### 1.1 销售收入定义

-   Revenue 使用订单明细层面的 `Sales` 字段计算。
-   Sales = Quantity × UnitPrice。
-   所有销售分析、客户分析、产品分析必须基于清洗后的数据：

`data/processed/cleaned_sales.csv`

------------------------------------------------------------------------

## 2. 非商品交易规则

以下交易类型不参与产品分析：

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

说明：

-   这些记录属于物流、费用、调整、样品或系统交易。
-   它们仍保留在销售总览和客户价值分析中。
-   它们仅从 Product Performance 和 Product Concentration 分析中排除。

------------------------------------------------------------------------
## 3. 产品分析规则

产品分析统一使用以下规则：

- `StockCode` 作为商品唯一标识。
- `StockCode` 在分析前统一执行：
  - 去除前后空格。
  - 转换为大写。
- `Description` 仅作为商品展示名称，不作为商品唯一标识或聚合键。
- 排除业务规则中定义的 10 个非商品交易编码。
- Revenue 按 `StockCode` 聚合并保留两位小数。

Top Product Revenue Share 使用：

Top N Product Revenue / Total Product Revenue × 100

当前冻结指标：

- Top 10 Product Revenue Share = **9.45%**
- Total Product Revenue = **10,270,813.87**
- Top 10 Product Revenue = **970,100.89**

一致性状态：

- Pandas / SQL Product Concentration Consistency：PASS

------------------------------------------------------------------------

## 4. 客户分析规则

Customer ID 是客户唯一标识。

客户指标：

### Recency

定义：

距离最后交易日期的天数。

公式：

Reference Date - Last Purchase Date

数值越小代表客户越活跃。

### Frequency

定义：

客户完成的独立订单数量。

使用：

COUNT(DISTINCT InvoiceNo)

### Monetary

定义：

客户累计消费金额。

使用：

SUM(Sales)

------------------------------------------------------------------------

## 5. RFM 分析规则

RFM 三个指标均采用五分制：

-   R Score：最近购买客户获得高分。
-   F Score：订单数量高获得高分。
-   M Score：消费金额高获得高分。

RFM Score：

R Score + F Score + M Score

------------------------------------------------------------------------

## 6. Customer Segment 定义

当前冻结客户分类：

### Champions

高活跃、高频、高消费客户。

### Loyal Customers

稳定购买客户。

### Regular Customers

普通客户。

### At Risk

历史价值较高但近期活跃下降客户。

### Lost Customers

长期未购买客户。

### High Value Lost

历史高价值但明显流失客户。

### Big Spenders

高消费客户。

------------------------------------------------------------------------

## 7. SQL 与 Pandas 一致性规则

Pandas Layer：

-   用于分析逻辑开发、验证和调试。

SQL Layer：

-   用于生产查询、Agent 调用和应用服务。

两层必须保持：

-   相同过滤规则。
-   相同字段定义。
-   相同业务逻辑。

------------------------------------------------------------------------
