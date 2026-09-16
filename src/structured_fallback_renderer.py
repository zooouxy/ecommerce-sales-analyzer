"""结构化Tool结果的最小确定性Fallback渲染器。"""

FIELD_LABELS = {
    "segment": "客户分群",
    "customer_count": "客户数量",
    "total_revenue": "总收入",
    "revenue": "收入",
    "revenue_percentage": "收入占比",
    "average_revenue_per_customer": "平均每位客户收入",
    "total_orders": "订单数",
    "orders": "订单数",
    "total_quantity": "总销量",
    "quantity": "销量",
    "average_order_value": "平均订单金额",
    "stock_code": "商品编号",
    "description": "商品名称",
    "month": "月份",
    "revenue_growth_pct": "收入环比",
    "is_partial_month": "是否为不完整月份",
    "entity_type": "实体类型",
    "stock_code_a": "商品A",
    "stock_code_b": "商品B",
    "segment_a": "客户分群A",
    "segment_b": "客户分群B",
    "higher_revenue_product": "收入更高的商品",
    "higher_quantity_product": "销量更高的商品",
    "higher_order_product": "订单数更高的商品",
    "higher_total_revenue_segment": "总收入更高的客户分群",
    "higher_customer_count_segment": "客户数量更多的客户分群",
    "higher_revenue_percentage_segment": "收入占比更高的客户分群",
    "higher_average_revenue_per_customer_segment": "平均客户收入更高的客户分群",
    "revenue_difference": "收入差值",
    "revenue_difference_pct": "收入差异比例",
    "quantity_difference": "销量差值",
    "quantity_difference_pct": "销量差异比例",
    "orders_difference": "订单数差值",
    "orders_difference_pct": "订单数差异比例",
    "customer_count_difference": "客户数量差值",
    "customer_count_difference_pct": "客户数量差异比例",
    "total_revenue_difference": "总收入差值",
    "total_revenue_difference_pct": "总收入差异比例",
    "revenue_percentage_difference_pp": "收入占比差值",
    "average_revenue_per_customer_difference": "平均客户收入差值",
    "average_revenue_per_customer_difference_pct": "平均客户收入差异比例",
    "left": "对象A",
    "right": "对象B",
    "comparison": "对比结果"
}

PERCENT_FIELDS = {
    "revenue_percentage",
    "revenue_growth_pct",
    "revenue_difference_pct",
    "quantity_difference_pct",
    "orders_difference_pct",
    "customer_count_difference_pct",
    "total_revenue_difference_pct",
    "average_revenue_per_customer_difference_pct"
}

POINT_FIELDS = {
    "revenue_percentage_difference_pp"
}

SKIP_FIELDS = {
    "missing_stock_codes",
    "missing_segments",
    "revenue_difference_semantics",
    "quantity_difference_semantics",
    "orders_difference_semantics",
    "customer_count_difference_semantics",
    "total_revenue_difference_semantics",
    "revenue_percentage_difference_semantics",
    "average_revenue_per_customer_difference_semantics"
}


class StructuredFallbackRenderer:
    """把已验证的结构化Tool结果转换为保守、可读的确定性文本。"""

    def render(self, tool_name, tool_result):
        if not isinstance(tool_result, dict):
            return None

        if tool_result.get("success") is not True:
            return None

        data = tool_result.get("data")

        if isinstance(data, dict):
            body = self._render_mapping(data)
        elif isinstance(data, list):
            body = self._render_records(data)
        else:
            return None

        if not body:
            return None

        return (
            "根据工具返回的结构化数据：\n\n"
            f"{body}"
        )

    def _render_records(self, records):
        valid_records = [
            record
            for record in records
            if isinstance(record, dict)
        ]

        if not valid_records:
            return None

        if len(valid_records) == 1:
            return self._render_mapping(valid_records[0])

        blocks = []

        for record in valid_records:
            block = self._render_mapping(record)

            if block:
                blocks.append(block)

        return "\n\n".join(blocks) if blocks else None

    def _render_mapping(self, mapping, level=0):
        lines = []

        for key, value in mapping.items():
            if key in SKIP_FIELDS or value is None:
                continue

            label = FIELD_LABELS.get(
                key,
                key.replace("_", " ")
            )

            if isinstance(value, dict):
                nested = self._render_mapping(
                    value,
                    level=level + 1
                )

                if nested:
                    lines.append(
                        f"{'#' * min(level + 3, 6)} {label}"
                    )
                    lines.append(nested)

                continue

            if isinstance(value, list):
                if not value:
                    continue

                nested = self._render_records(value)

                if nested:
                    lines.append(
                        f"{'#' * min(level + 3, 6)} {label}"
                    )
                    lines.append(nested)

                continue

            lines.append(
                f"- {label}：{self._format_value(key, value)}"
            )

        return "\n".join(lines)

    def _format_value(self, key, value):
        if isinstance(value, bool):
            return "是" if value else "否"

        if key in PERCENT_FIELDS and isinstance(value, (int, float)):
            return f"{value:.2f}%"

        if key in POINT_FIELDS and isinstance(value, (int, float)):
            return f"{value:.2f} 个百分点"

        if isinstance(value, int):
            return f"{value:,}"

        if isinstance(value, float):
            return f"{value:,.2f}"

        return str(value)
