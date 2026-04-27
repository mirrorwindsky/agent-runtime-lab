"""
规则版 Router。

模块职责：
1. 在没有 LLM Planner 的 Phase 1 中，将用户输入映射为 AgentAction。
2. 提供稳定、可测试的能力选择逻辑。
3. 为后续替换为 LLM Planner 保留相同输出结构。

当前限制：
- 仅支持少量显式命令前缀。
- 不做自然语言理解，也不做多步规划。
"""

from agent_runtime_lab.schemas.action import AgentAction


class RouterError(ValueError):
    """Router 无法生成可执行 action 时抛出的异常。"""


class SimpleRouter:
    """
    Phase 1 使用的确定性规则路由器。

    支持命令：
    - `calculate <expression>` 或 `calc <expression>`
    - `read <path>` 或 `read_file <path>`
    """

    _calculator_prefixes = ("calculate ", "calc ")
    _file_read_prefixes = ("read ", "read_file ")

    def route(self, user_input: str) -> AgentAction:
        text = user_input.strip()
        if not text:
            raise RouterError("User input cannot be empty")

        lowered = text.lower()

        for prefix in self._calculator_prefixes:
            if lowered.startswith(prefix):
                expression = text[len(prefix) :].strip()
                if not expression:
                    raise RouterError("Calculator command requires an expression")
                return AgentAction(
                    capability_name="local.calculator",
                    arguments={"expression": expression},
                    reason="Matched calculator command prefix.",
                )

        for prefix in self._file_read_prefixes:
            if lowered.startswith(prefix):
                path = text[len(prefix) :].strip()
                if not path:
                    raise RouterError("File read command requires a path")
                return AgentAction(
                    capability_name="local.file_read",
                    arguments={"path": path},
                    reason="Matched file read command prefix.",
                )

        raise RouterError("Unsupported input. Expected command prefixes: calc, calculate, read")
