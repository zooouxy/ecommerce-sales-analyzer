import pandas as pd
import streamlit as st

from src.agent import EcommerceAgent
from src.query_service import (
    get_customer_segments,
    get_customer_value,
    get_monthly_sales,
    get_product_concentration,
    get_product_performance,
    get_sales_kpi
)


st.set_page_config(
    page_title="AI Ecommerce Analyst",
    page_icon="📊",
    layout="wide"
)


@st.cache_resource
def load_agent():
    """创建并缓存AI Analyst Agent。"""
    return EcommerceAgent()


def load_sales_kpi():
    """加载整体销售核心指标。"""
    return get_sales_kpi()


def load_monthly_sales():
    """加载并整理月度销售数据。"""
    records = get_monthly_sales()
    df = pd.DataFrame(records)

    if df.empty:
        return df

    df["month"] = pd.to_datetime(
        df["month"],
        format="%Y-%m"
    )

    return df.sort_values("month")


def load_product_performance(limit=None, stock_code=None):
    """加载商品表现数据。"""
    records = get_product_performance(
        limit=limit,
        stock_code=stock_code
    )

    return pd.DataFrame(records)


def load_product_concentration():
    """加载商品收入集中度指标。"""
    return get_product_concentration()


def load_customer_segments(segment=None):
    """加载客户分群数据。"""
    records = get_customer_segments(
        segment=segment
    )

    return pd.DataFrame(records)


def load_customer_value(limit=None, customer_id=None):
    """加载客户价值数据。"""
    records = get_customer_value(
        limit=limit,
        customer_id=customer_id
    )

    return pd.DataFrame(records)


def render_sidebar():
    """渲染侧边栏导航和项目说明。"""
    st.sidebar.title("📊 AI Ecommerce Analyst")
    st.sidebar.caption(
        "Interactive ecommerce analytics powered by "
        "structured data and an AI Agent."
    )

    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigation",
        [
            "Executive Overview",
            "Product Analysis",
            "Customer Analysis",
            "AI Analyst"
        ]
    )

    st.sidebar.divider()

    st.sidebar.markdown("**Analytics Architecture**")
    st.sidebar.caption(
        "Streamlit → Query Service → SQL / SQLite"
    )
    st.sidebar.caption(
        "AI Analyst → Tools → Query Service → SQL / SQLite"
    )

    monthly_df = load_monthly_sales()

    if not monthly_df.empty:
        start_month = monthly_df["month"].min().strftime("%Y-%m")
        end_month = monthly_df["month"].max().strftime("%Y-%m")

        st.sidebar.markdown("**Data Coverage**")
        st.sidebar.caption(
            f"{start_month} → {end_month}"
        )

    return page


def render_executive_overview():
    """渲染销售概览页面。"""
    st.title("Executive Overview")
    st.caption(
        "High-level ecommerce performance, order activity, "
        "and monthly revenue trends."
    )

    kpi = load_sales_kpi()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Revenue",
        f"{kpi['total_revenue']:,.2f}"
    )

    col2.metric(
        "Total Orders",
        f"{kpi['total_orders']:,}"
    )

    col3.metric(
        "Total Quantity",
        f"{kpi['total_quantity']:,}"
    )

    col4.metric(
        "Average Order Value",
        f"{kpi['average_order_value']:,.2f}"
    )

    st.divider()

    monthly_df = load_monthly_sales()

    if monthly_df.empty:
        st.info("No monthly sales data available.")
        return

    st.subheader("Monthly Revenue Trend")
    st.caption(
        "Revenue performance across the available transaction period."
    )

    revenue_chart = monthly_df.set_index(
        "month"
    )[["revenue"]]

    st.line_chart(
        revenue_chart,
        use_container_width=True
    )

    st.subheader("Monthly Sales Details")

    display_df = monthly_df.copy()

    display_df["month"] = display_df[
        "month"
    ].dt.strftime("%Y-%m")

    display_df["revenue"] = display_df[
        "revenue"
    ].map(
        lambda value: f"{value:,.2f}"
    )

    display_df["orders"] = display_df[
        "orders"
    ].map(
        lambda value: f"{value:,}"
    )

    display_df[
        "revenue_growth_pct"
    ] = display_df[
        "revenue_growth_pct"
    ].map(
        lambda value: (
            ""
            if pd.isna(value)
            else f"{value:.2f}%"
        )
    )

    display_df = display_df.rename(
        columns={
            "month": "Month",
            "revenue": "Revenue",
            "orders": "Orders",
            "revenue_growth_pct": "Revenue Growth"
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


def render_product_analysis():
    """渲染商品分析页面。"""
    st.title("Product Analysis")
    st.caption(
        "Explore product revenue, sales volume, ranking, "
        "and revenue concentration."
    )

    concentration = load_product_concentration()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Product Revenue",
        f"{concentration['total_product_revenue']:,.2f}"
    )

    col2.metric(
        "Top 10 Revenue",
        f"{concentration['top_10_revenue']:,.2f}"
    )

    col3.metric(
        "Top 10 Revenue Share",
        f"{concentration['top_10_revenue_share_pct']:.2f}%"
    )

    st.divider()

    st.subheader("Top 10 Products by Revenue")
    st.caption(
        "Highest-revenue products ranked by StockCode."
    )

    top_products_df = load_product_performance(
        limit=10
    )

    if top_products_df.empty:
        st.info("No product performance data available.")
    else:
        chart_df = top_products_df[
            [
                "stock_code",
                "revenue"
            ]
        ].set_index(
            "stock_code"
        )

        st.bar_chart(
            chart_df,
            use_container_width=True
        )

        display_df = top_products_df.copy()

        display_df["revenue"] = display_df[
            "revenue"
        ].map(
            lambda value: f"{value:,.2f}"
        )

        display_df["quantity"] = display_df[
            "quantity"
        ].map(
            lambda value: f"{int(value):,}"
        )

        display_df["orders"] = display_df[
            "orders"
        ].map(
            lambda value: f"{int(value):,}"
        )

        display_df = display_df.rename(
            columns={
                "stock_code": "StockCode",
                "description": "Description",
                "revenue": "Revenue",
                "quantity": "Quantity",
                "orders": "Orders"
            }
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.subheader("Product Lookup")
    st.caption(
        "Enter a StockCode to inspect one product in detail."
    )

    stock_code = st.text_input(
        "StockCode",
        placeholder="e.g. 22423"
    ).strip()

    if stock_code:
        product_df = load_product_performance(
            stock_code=stock_code
        )

        if product_df.empty:
            st.warning(
                f"No product performance data found "
                f"for StockCode {stock_code}."
            )
        else:
            product = product_df.iloc[0]

            st.markdown(
                f"### {product['description']}"
            )

            st.caption(
                f"StockCode: {product['stock_code']}"
            )

            p1, p2, p3 = st.columns(3)

            p1.metric(
                "Revenue",
                f"{product['revenue']:,.2f}"
            )

            p2.metric(
                "Quantity",
                f"{int(product['quantity']):,}"
            )

            p3.metric(
                "Orders",
                f"{int(product['orders']):,}"
            )


def render_customer_analysis():
    """渲染客户分析页面。"""
    st.title("Customer Analysis")
    st.caption(
        "Understand customer segmentation, revenue contribution, "
        "and individual customer value."
    )

    segments_df = load_customer_segments()

    if segments_df.empty:
        st.info("No customer segment data available.")
        return

    total_customers = int(
        segments_df["customer_count"].sum()
    )

    total_segment_revenue = segments_df[
        "total_revenue"
    ].sum()

    largest_segment = segments_df.loc[
        segments_df["customer_count"].idxmax()
    ]

    highest_revenue_segment = segments_df.loc[
        segments_df["total_revenue"].idxmax()
    ]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Customers",
        f"{total_customers:,}"
    )

    col2.metric(
        "Segment Revenue",
        f"{total_segment_revenue:,.2f}"
    )

    col3.metric(
        "Largest Segment",
        largest_segment["segment"]
    )

    col4.metric(
        "Highest Revenue Segment",
        highest_revenue_segment["segment"]
    )

    st.divider()

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Customers by Segment")
        st.caption(
            "Customer distribution across RFM segments."
        )

        customer_chart = segments_df[
            [
                "segment",
                "customer_count"
            ]
        ].set_index(
            "segment"
        )

        st.bar_chart(
            customer_chart,
            use_container_width=True
        )

    with chart_col2:
        st.subheader("Revenue by Segment")
        st.caption(
            "Revenue contribution from each customer segment."
        )

        revenue_chart = segments_df[
            [
                "segment",
                "total_revenue"
            ]
        ].set_index(
            "segment"
        )

        st.bar_chart(
            revenue_chart,
            use_container_width=True
        )

    st.subheader("Customer Segment Details")

    display_df = segments_df.copy()

    display_df["customer_count"] = display_df[
        "customer_count"
    ].map(
        lambda value: f"{int(value):,}"
    )

    display_df["total_revenue"] = display_df[
        "total_revenue"
    ].map(
        lambda value: f"{value:,.2f}"
    )

    display_df["revenue_percentage"] = display_df[
        "revenue_percentage"
    ].map(
        lambda value: f"{value:.2f}%"
    )

    display_df[
        "average_revenue_per_customer"
    ] = display_df[
        "average_revenue_per_customer"
    ].map(
        lambda value: f"{value:,.2f}"
    )

    display_df = display_df.rename(
        columns={
            "segment": "Segment",
            "customer_count": "Customers",
            "total_revenue": "Revenue",
            "revenue_percentage": "Revenue Share",
            "average_revenue_per_customer": "Avg Revenue / Customer"
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Customer Lookup")
    st.caption(
        "Enter a Customer ID to inspect customer-level value metrics."
    )

    customer_id_text = st.text_input(
        "Customer ID",
        placeholder="e.g. 14646"
    ).strip()

    if customer_id_text:
        try:
            customer_id = int(
                customer_id_text
            )
        except ValueError:
            st.warning(
                "Customer ID must be a positive integer."
            )
            return

        if customer_id <= 0:
            st.warning(
                "Customer ID must be a positive integer."
            )
            return

        customer_df = load_customer_value(
            customer_id=customer_id
        )

        if customer_df.empty:
            st.warning(
                f"No customer value data found "
                f"for Customer ID {customer_id}."
            )
        else:
            customer = customer_df.iloc[0]

            st.markdown(
                f"### Customer {int(customer['customer_id'])}"
            )

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Total Orders",
                f"{int(customer['total_orders']):,}"
            )

            c2.metric(
                "Total Revenue",
                f"{customer['total_revenue']:,.2f}"
            )

            c3.metric(
                "Average Order Value",
                f"{customer['average_order_value']:,.2f}"
            )

            st.caption(
                f"Purchase period: "
                f"{customer['first_purchase_date']} "
                f"→ {customer['last_purchase_date']}"
            )


def render_agent_trace(trace):
    """渲染Agent执行轨迹。"""
    with st.expander(
        "Agent Trace",
        expanded=False
    ):
        tool_calls = trace.get(
            "tool_calls",
            []
        )

        tool_results = trace.get(
            "tool_results",
            []
        )

        grounding = trace.get(
            "grounding"
        )

        st.markdown("#### Tool Calls")

        if tool_calls:
            st.json(tool_calls)
        else:
            st.caption(
                "No analytical tool call was required."
            )

        st.markdown("#### Tool Results")

        if tool_results:
            st.json(tool_results)
        else:
            st.caption(
                "No tool result was returned."
            )

        st.markdown("#### Grounding Validation")

        if grounding is None:
            st.caption(
                "Grounding validation was not required."
            )
            return

        if grounding["passed"]:
            st.success(
                "Grounding validation passed."
            )
        else:
            st.warning(
                "Grounding validation returned warnings. "
                "Review the evidence below."
            )

        st.json(grounding)


def render_ai_analyst():
    """渲染AI Analyst对话页面。"""
    st.title("AI Analyst")
    st.caption(
        "Ask ecommerce business questions in natural language. "
        "The Agent selects analytical tools and answers from "
        "structured query results."
    )

    with st.expander(
        "Example Questions",
        expanded=True
    ):
        st.markdown(
            """
- 2011年11月销售情况怎么样？
- 商品22423的销售表现怎么样？
- Champions客户贡献了多少收入？
- 整体销售收入是多少，同时Top 10商品占整体商品收入多少？
"""
        )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if st.session_state.chat_history:
        if st.button(
            "Clear Conversation",
            type="secondary"
        ):
            st.session_state.chat_history = []
            st.rerun()

    for message in st.session_state.chat_history:
        with st.chat_message(
            message["role"]
        ):
            st.markdown(
                message["content"]
            )

            if (
                message["role"] == "assistant"
                and message.get("trace")
            ):
                render_agent_trace(
                    message["trace"]
                )

    question = st.chat_input(
        "Ask the AI Ecommerce Analyst..."
    )

    if not question:
        return

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner(
            "Analyzing ecommerce data..."
        ):
            try:
                agent = load_agent()

                trace = agent.ask_with_trace(
                    question
                )

                answer = trace["answer"]

                st.markdown(answer)

                render_agent_trace(
                    trace
                )

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "trace": trace
                    }
                )

            except Exception:
                error_message = (
                    "The AI Analyst could not complete this request. "
                    "Please try again with a more focused question."
                )

                st.error(error_message)

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": error_message
                    }
                )


def main():
    page = render_sidebar()

    if page == "Executive Overview":
        render_executive_overview()

    elif page == "Product Analysis":
        render_product_analysis()

    elif page == "Customer Analysis":
        render_customer_analysis()

    elif page == "AI Analyst":
        render_ai_analyst()


if __name__ == "__main__":
    main()