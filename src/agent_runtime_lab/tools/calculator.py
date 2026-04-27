"""
本地计算器能力。

模块职责：
1. 提供一个可注册到 CapabilityRegistry 的安全算术计算能力。
2. 使用 Python AST 白名单解析表达式，避免 unrestricted eval 的执行风险。
3. 作为 Phase 1 本地工具能力的参考实现。

当前限制：
- 仅支持数字字面量和基础算术运算。
- 不支持变量、函数调用、属性访问或容器字面量。
"""

import ast
import operator
from typing import Any

from agent_runtime_lab.capabilities.base import BaseCapability
from agent_runtime_lab.schemas.capability import CapabilitySpec


class CalculatorError(ValueError):
    """计算器能力执行失败时抛出的异常。"""


class CalculatorCapability(BaseCapability):
    """安全算术表达式计算能力。"""

    _binary_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    _unary_operators = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def spec(self) -> CapabilitySpec:
        return CapabilitySpec(
            name="local.calculator",
            capability_type="local_tool",
            description="安全计算基础算术表达式。",
            input_schema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "待计算的算术表达式，例如 `1 + 2 * (3 + 4)`。",
                    },
                },
                "required": ["expression"],
                "additionalProperties": False,
            },
            output_schema={
                "type": "object",
                "properties": {
                    "result": {"type": "number"},
                },
                "required": ["result"],
            },
            risk_level="low",
        )

    async def arun(self, arguments: dict[str, Any], context: dict[str, Any]) -> int | float:
        expression = arguments.get("expression")
        if not isinstance(expression, str) or not expression.strip():
            raise CalculatorError("Calculator requires a non-empty string argument: expression")

        return self.evaluate(expression)

    def evaluate(self, expression: str) -> int | float:
        """解析并计算安全算术表达式。"""

        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as exc:
            raise CalculatorError(f"Invalid arithmetic expression: {expression}") from exc

        return self._evaluate_node(tree.body)

    def _evaluate_node(self, node: ast.AST) -> int | float:
        if isinstance(node, ast.Constant):
            return self._evaluate_constant(node)

        if isinstance(node, ast.BinOp):
            operator_type = type(node.op)
            if operator_type not in self._binary_operators:
                raise CalculatorError(f"Unsupported binary operator: {operator_type.__name__}")

            left = self._evaluate_node(node.left)
            right = self._evaluate_node(node.right)
            return self._binary_operators[operator_type](left, right)

        if isinstance(node, ast.UnaryOp):
            operator_type = type(node.op)
            if operator_type not in self._unary_operators:
                raise CalculatorError(f"Unsupported unary operator: {operator_type.__name__}")

            operand = self._evaluate_node(node.operand)
            return self._unary_operators[operator_type](operand)

        raise CalculatorError(f"Unsupported expression node: {type(node).__name__}")

    def _evaluate_constant(self, node: ast.Constant) -> int | float:
        if isinstance(node.value, bool) or not isinstance(node.value, int | float):
            raise CalculatorError(f"Unsupported literal value: {node.value!r}")

        return node.value
