"""
Business Rules Definition

集中管理项目中的业务规则。
包括：
— 商品分析排除的非商品交易编码
- RFM评分规则
- Customer Segment分类规则

所有Python分析和SQL逻辑应该保持与这里一致。
"""

# 商品分析排除的非商品交易编码
EXCLUDED_PRODUCT_STOCK_CODES = [
    "DOT",
    "POST",
    "M",
    "AMAZONFEE",
    "B",
    "C2",
    "23444",
    "BANK CHARGES",
    "23574",
    "S"
]
# ===============================
# Recency Score Rules
# 越近购买，分数越高
# ===============================

RECENCY_RULES = [
    {"max_days": 12, "score": 5},
    {"max_days": 32, "score": 4},
    {"max_days": 71, "score": 3},
    {"max_days": 178, "score": 2},
    {"max_days": None, "score": 1}
]


# ===============================
# Frequency Score Rules
# 订单次数越多，分数越高
# ===============================

FREQUENCY_RULES = [
    {"min_orders": 8, "score": 5},
    {"min_orders": 4, "score": 4},
    {"min_orders": 3, "score": 3},
    {"min_orders": 2, "score": 2},
    {"min_orders": None, "score": 1}
]


# ===============================
# Monetary Score Rules
# 消费金额越高，分数越高
# ===============================

MONETARY_RULES = [
    {"min_amount": 5000, "score": 5},
    {"min_amount": 2000, "score": 4},
    {"min_amount": 800, "score": 3},
    {"min_amount": 300, "score": 2},
    {"min_amount": None, "score": 1}
]


# ===============================
# Customer Segment Rules
# ===============================

SEGMENT_RULES = {
    "Champions": {
        "r_score": [5],
        "f_score": [5],
        "m_score": [5]
    },
    "Loyal Customers": {
        "r_score_min": 4,
        "f_score_min": 4
    },
    "Big Spenders": {
        "r_score_min": 4,
        "m_score": [5],
        "f_score_max": 3
    },
    "High Value Lost": {
        "r_score_max": 2,
        "m_score_min": 4
    },
    "At Risk": {
        "r_score_max": 2,
        "f_score_min": 3
    },
    "Lost Customers": {
        "r_score_max": 2,
        "f_score_max": 2,
        "m_score_max": 2
    },
    "Regular Customers": {
        "default": True
    }
}