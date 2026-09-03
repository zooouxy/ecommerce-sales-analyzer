from src.tool_registry import execute_tool


def run_tool(name, arguments=None):
    """统一执行Tool，并返回标准结果结构。"""
    if arguments is None:
        arguments = {}

    if not isinstance(arguments, dict):
        return {
            "success": False,
            "tool": name,
            "error_type": "TypeError",
            "error": "arguments must be a dictionary"
        }

    try:
        result = execute_tool(
            name,
            **arguments
        )

        return {
            "success": True,
            "tool": name,
            "data": result
        }

    except Exception as exc:
        return {
            "success": False,
            "tool": name,
            "error_type": type(exc).__name__,
            "error": str(exc)
        }