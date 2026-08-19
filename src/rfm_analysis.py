import pandas as pd


def calculate_recency(df):
    """
    计算每个客户距离最近一次购买的天数。
    """

    # 使用整个数据集中的最后交易日期作为参考日期
    reference_date = df["InvoiceDate"].max()

    # 按客户分组，找出每个客户最后一次购买的日期
    last_purchase = (
        df.groupby("CustomerID")["InvoiceDate"].max()
    )

    # 计算参考日期与客户最后购买日期之间相差多少天
    recency = (
        reference_date - last_purchase
    ).dt.days

    # 按 Recency 从小到大排序
    # 数值越小，说明客户最近购买过，活跃程度通常越高
    return recency.sort_values()

def calculate_frequency(df):
    """
    计算每个客户的购买频率/订单数量
    """

    # 先按CustomerID分组，统计每个客户有多少不同订单
    # 使用nunique()，避免同一订单的多个商品被重复计算
    frequency = (
        df.groupby("CustomerID")["InvoiceNo"].nunique()
    )

    # 按订单数量从大到小排列
    # 订单越多说明客户购买频率越高
    return frequency.sort_values(ascending=False)

def calculate_monetary(df):
    """
        计算每个客户的消费总额
        """

    # 按CustomerID分组，计算每个客户的sales总和
    # 得到每个客户在数据集中的累计消费总额
    monetary = (
        df.groupby("CustomerID")["Sales"].sum()
    )
    
    # 按消费总额从高到低排序
    # 金额越高。说明客户的历史价值通常越高
    return monetary.sort_values(ascending=False)

def build_rfm_table(df):
    """
    将 Recency、Frequency、Monetary 三个指标合并成一个 RFM 表。
    """

    # 计算 R：距离最近一次购买的天数
    recency = calculate_recency(df)

    # 计算 F：不同订单的数量
    frequency = calculate_frequency(df)

    # 计算 M：累计消费金额
    monetary = calculate_monetary(df)

    # 将三个指标按照 CustomerID 对齐并合并
    rfm = pd.concat(
        [
            recency.rename("Recency"),
            frequency.rename("Frequency"),
            monetary.rename("Monetary")
        ],
        axis=1
    )

    # 删除 R、F、M 任意一个指标缺失的客户
    # 理论上正常客户都应该同时拥有三个指标
    rfm = rfm.dropna()

    return rfm

def calculate_rfm_scores(rfm):
    """
    根据 RFM 指标为客户进行 1-5 分评分。
    """

    # Recency：数值越小越好
    # 使用 qcut 将客户按照 Recency 分成 5 个等级
    # 通过 ascending=False 让最近购买的客户获得更高分
    r_score = pd.qcut(
        rfm["Recency"].rank(method="first"),
        5,
        labels=[5, 4, 3, 2, 1]
    )

    # Frequency：数值越大越好
    # 购买频率越高，获得的分数越高
    f_score = pd.qcut(
        rfm["Frequency"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5]
    )

    # Monetary：数值越大越好
    # 消费金额越高，获得的分数越高
    m_score = pd.qcut(
        rfm["Monetary"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5]
    )

    # 将三个评分加入 RFM 表
    rfm["R_Score"] = r_score.astype(int)
    rfm["F_Score"] = f_score.astype(int)
    rfm["M_Score"] = m_score.astype(int)

    # 计算总 RFM Score
    # 分数范围为 3-15
    rfm["RFM_Score"] = (
        rfm["R_Score"]
        + rfm["F_Score"]
        + rfm["M_Score"]
    )

    return rfm

def show_rfm_score_ranges(rfm):
    """
    查看 R、F、M 三个指标对应的实际评分范围。
    """

    # 计算 Recency 五分位数边界
    # Recency 越小越好，所以重点观察较小的数值范围
    recency_ranges = rfm["Recency"].quantile(
        [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    )

    # 计算 Frequency 五分位数边界
    # Frequency 越大越好
    frequency_ranges = rfm["Frequency"].quantile(
        [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    )

    # 计算 Monetary 五分位数边界
    # Monetary 越大越好
    monetary_ranges = rfm["Monetary"].quantile(
        [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    )

    print("\nRFM Score Ranges")
    print("----------------")

    print("\nRecency:")
    print(recency_ranges)

    print("\nFrequency:")
    print(frequency_ranges)

    print("\nMonetary:")
    print(monetary_ranges)


def assign_customer_segment(rfm):
    """
    根据 RFM Score 和 R/F/M 评分组合对客户进行分层。
    """

    # 创建客户分层函数
    def segment_customer(row):

        # R、F、M 都达到最高等级
        # 表示客户最近购买、购买频繁、消费金额也高
        if (
            row["R_Score"] >= 4
            and row["F_Score"] >= 4
            and row["M_Score"] >= 4
        ):
            return "High Value"

        # 最近购买较少，但历史购买频率和消费金额较高
        # 这类客户可能正在流失，需要重点关注
        elif (
            row["R_Score"] <= 2
            and row["F_Score"] >= 4
            and row["M_Score"] >= 4
        ):
            return "At Risk"

        # 最近购买比较活跃，但购买频率和消费金额一般
        # 可能是有潜力进一步培养的客户
        elif (
            row["R_Score"] >= 4
            and row["F_Score"] <= 3
            and row["M_Score"] <= 3
        ):
            return "Potential"

        # 其他客户暂时归入普通客户
        else:
            return "Regular"

    # 将分层规则应用到每一个客户
    rfm["Segment"] = rfm.apply(
        segment_customer,
        axis=1
    )

    return rfm

def summarize_customer_segments(rfm):
    """
    汇总不同客户群体的客户数量、销售额、收入占比和平均客户收入。
    """

    # 按客户分层统计客户数量和总消费金额
    segment_summary = (
        rfm.groupby("Segment")
        .agg(
            Customer_Count=("Monetary", "count"),
            Total_Revenue=("Monetary", "sum")
        )
    )

    # 计算所有客户的总收入
    total_revenue = segment_summary["Total_Revenue"].sum()

    # 计算每个客户群的收入占比
    segment_summary["Revenue_Percentage"] = (
        segment_summary["Total_Revenue"]
        / total_revenue
        * 100
    )
    # 计算每个客户群的平均历史收入
    segment_summary["Average_Revenue_Per_Customer"] = (
            segment_summary["Total_Revenue"]
            / segment_summary["Customer_Count"]
    )

    # 按收入贡献从高到低排序
    segment_summary = segment_summary.sort_values(
        "Total_Revenue",
        ascending=False
    )

    return segment_summary

def generate_business_insights(segment_summary):
    """
    根据客户分层汇总结果生成 Business Insights Summary。
    """

    # 获取 High Value 客户的数据
    high_value = segment_summary.loc["High Value"]

    # 获取 At Risk 客户的数据
    at_risk = segment_summary.loc["At Risk"]

    # 获取 Potential 客户的数据
    potential = segment_summary.loc["Potential"]

    # 计算 High Value 客户占全部 RFM 客户的比例
    high_value_customer_percentage = (
        high_value["Customer_Count"]
        / segment_summary["Customer_Count"].sum()
        * 100
    )

    # 创建 Business Insights 字典
    insights = {
        "Revenue Concentration": (
            f"High Value customers represent "
            f"{high_value_customer_percentage:.2f}% of customers "
            f"but contribute "
            f"{high_value['Revenue_Percentage']:.2f}% of total revenue."
        ),

        "Customer Retention Risk": (
            f"At Risk customers contribute "
            f"{at_risk['Revenue_Percentage']:.2f}% of total revenue "
            f"with an average historical revenue of "
            f"{at_risk['Average_Revenue_Per_Customer']:.2f} "
            f"per customer."
        ),

        "Growth Opportunity": (
            f"Potential customers account for "
            f"{potential['Customer_Count']:.0f} customers "
            f"but contribute only "
            f"{potential['Revenue_Percentage']:.2f}% of total revenue."
        )
    }

    return insights