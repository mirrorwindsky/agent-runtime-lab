"""
Agent action 数据结构。

模块职责：
1. 表示 Planner 或 Router 选择出的下一步能力调用。
2. 将用户输入解析结果传递给 Runtime 执行层。
3. 为后续 LLM Planner、审批流和追踪系统保留稳定结构。
"""

from typing import Any

from pydantic import BaseModel, Field


class AgentAction(BaseModel):
    """
    Runtime 可执行的能力调用计划。

    字段说明：
    - capability_name: 目标能力名称，必须能在 CapabilityRegistry 中解析。
    - arguments: 传给能力的结构化参数。
    - reason: 选择该能力的简短原因，便于调试和追踪。
    """

    capability_name: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    reason: str | None = None
