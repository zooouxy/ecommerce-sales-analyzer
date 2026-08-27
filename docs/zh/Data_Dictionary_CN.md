AI电商分析系统数据字典
1. 文档概述
本文档定义 AI Ecommerce Analyst 系统的数据结构、业务实体、字段含义及数据关系。
该数据字典作为系统数据模型设计和分析能力构建的基础。
2. 数据领域模型
系统核心业务实体包括：

Customer：客户维度信息。
Transaction：交易事实数据。
Product：商品维度信息。

实体关系：

Customer 1:N Transaction
Product 1:N Transaction
3. 客户实体
用途：
存储客户基础信息。

字段：
CustomerID | INTEGER | 客户唯一标识
Country | VARCHAR | 客户所在国家

业务用途：
- 客户画像
- 客户分群
- 地理市场分析
4. 交易实体
用途：
记录订单商品级交易行为。

字段：
InvoiceNo | VARCHAR | 订单编号
InvoiceDate | DATE | 交易时间
CustomerID | INTEGER | 客户编号
StockCode | VARCHAR | 商品编号
Quantity | INTEGER | 商品数量
UnitPrice | DECIMAL | 商品单价
Sales | DECIMAL | 交易收入

业务用途：
- 销售分析
- 收入计算
- 客户价值分析
- 商品表现分析
5. 产品实体
用途：
存储商品信息。

字段：
StockCode | VARCHAR | 商品编号
Description | VARCHAR | 商品名称

可扩展字段：
Category、Supplier、Cost
6. 数据质量规则
主要规则：

- CustomerID 应保持唯一性
- 日期字段必须符合标准日期格式
- Quantity 应为有效正数
- Sales 应满足业务计算规则
7. 数据扩展设计
未来可扩展：

- 客户行为数据
- 商品分类数据
- 营销活动数据
- 供应链数据