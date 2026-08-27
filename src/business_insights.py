
def generate_sales_insights(monthly_sales):
    """
    根据月销售趋势生成销售洞察。
    """
    insights = []
# 找最高销售月份
    peak_month = (
        monthly_sales
        .idxmax()
    )
# 找最高销售额
    peak_revenue = (
        monthly_sales
        .max()
    )

    insights.append(
        "1.Sales Performance\n"
        "--------------------\n"
        f"Peak sales occurred in {peak_month}, "
        f"with revenue of {peak_revenue:.2f}."
    )

    return insights

def generate_customer_insights(segment_summary):
    """
    根据客户分群汇总结果生成 Customer Insights。
    """
    insights = []

    total_customers = segment_summary["Customer_Count"].sum()
    top_segment = segment_summary["Total_Revenue"].idxmax()
    top_revenue_share = segment_summary.loc[top_segment, "Revenue_Percentage"]
    top_customer_count = segment_summary.loc[top_segment, "Customer_Count"]
    top_customer_percentage = top_customer_count / total_customers * 100

    insights.append(
        "2.Customer Value\n"
        "-------------------------\n"
        f"{top_segment} customers represent {top_customer_percentage:.2f}% of customers "
        f"but contribute {top_revenue_share:.2f}% of total revenue."
    )

    if "High Value Lost" in segment_summary.index:
        lost = segment_summary.loc["High Value Lost"]
        insights.append(
            "3.High Value Customer Retention Risk\n"
            "-------------------------------------\n"
            f"High Value Lost customers represent {lost['Customer_Count']:.0f} customers "
            f"and contribute {lost['Revenue_Percentage']:.2f}% of revenue, "
            "indicating a potential customer reactivation opportunity."
        )

    if "At Risk" in segment_summary.index:
        at_risk = segment_summary.loc["At Risk"]
        insights.append(
            "4.Customer Retention Risk\n"
            "--------------------------\n"
            f"At Risk customers represent {at_risk['Customer_Count']:.0f} customers "
            f"and contribute {at_risk['Revenue_Percentage']:.2f}% of revenue, "
            f"with average historical revenue of {at_risk['Average_Revenue_Per_Customer']:.2f} per customer."
        )

    if "Big Spenders" in segment_summary.index:
        big_spenders = segment_summary.loc["Big Spenders"]
        insights.append(
            "5.High Value Low Frequency Customers\n"
            "-------------------------------------\n"
            f"Big Spenders contribute {big_spenders['Revenue_Percentage']:.2f}% of revenue "
            f"with average historical revenue of {big_spenders['Average_Revenue_Per_Customer']:.2f} per customer."
        )

    return insights

def generate_market_insights(country_analysis):
    """
    根据国家销售分析生成市场洞察。
    """
    insights = []

    top_country = country_analysis.index[0]

    share = country_analysis.iloc[0][
        "Revenue_Percentage"]

    insights.append(
        "5.Market Concentration\n"
        "----------------------\n"
        f"{top_country} contributes "
        f"{share:.2f}% of total revenue."
    )
    return insights


def generate_product_insights(top10_share):
    """
    根据产品集中度生成洞察。
    """

    insights = []

    insights.append(
        "6.Product Portfolio\n"
        "--------------------\n"
        f"Top 10 products contribute "
        f"{top10_share:.2f}% of product revenue, "
        "indicating a diversified product portfolio."
    )
    return insights


def generate_business_insights(monthly_sales, segment_summary, country_analysis, top10_share):
    """
    汇总所有 Business Insights。
    """
    insights = []
    insights.extend(generate_sales_insights(monthly_sales))
    insights.extend(generate_customer_insights(segment_summary))
    insights.extend(generate_market_insights(country_analysis))
    insights.extend(generate_product_insights(top10_share))
    return insights
