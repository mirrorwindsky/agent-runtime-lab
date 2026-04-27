"""
Agent Runtime 编排器。

模块职责：
1. 接收用户输入并调用 Router 生成 AgentAction。
2. 从 CapabilityRegistry 中解析并执行目标能力。
3. 将能力结果包装为 Observation 和 AgentResult。

设计说明：
- Runtime 只负责流程编排，不包含具体能力的业务逻辑。
- Planner/Router 可以后续替换为 LLM 实现，Runtime 主流程保持稳定。
"""

from typing import Any

from agent_runtime_lab.capabilities.registry import CapabilityRegistry
from agent_runtime_lab.runtime.planner import SimpleRouter
from agent_runtime_lab.schemas.observation import Observation
from agent_runtime_lab.schemas.state import AgentResult


class AgentRuntime:
    """Phase 1 最小 Runtime。"""

    def __init__(self, registry: CapabilityRegistry, router: SimpleRouter | None = None) -> None:
        self._registry = registry
        self._router = router or SimpleRouter()

    async def arun(self, user_input: str, context: dict[str, Any] | None = None) -> AgentResult:
        """
        执行单轮用户输入。

        当前流程：
        user_input -> SimpleRouter -> CapabilityRegistry -> Capability -> AgentResult
        """

        runtime_context = context or {}
        action = self._router.route(user_input)
        capability = self._registry.get(action.capability_name)

        try:
            result = await capability.arun(action.arguments, runtime_context)
        except Exception as exc:
            observation = Observation(
                capability_name=action.capability_name,
                success=False,
                error=str(exc),
            )
            return AgentResult(
                final_response=f"Capability execution failed: {exc}",
                action=action,
                observation=observation,
            )

        observation = Observation(
            capability_name=action.capability_name,
            success=True,
            result=result,
        )
        return AgentResult(
            final_response=str(result),
            action=action,
            observation=observation,
        )
