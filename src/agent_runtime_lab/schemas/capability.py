"""
Capability 相关数据结构。

模块职责：
1. 定义 Runtime 可识别的能力描述格式。
2. 为 Planner、Router 和 Registry 提供稳定的能力元数据。
3. 将能力的执行接口和能力说明解耦。

设计说明：
- `CapabilitySpec` 只描述能力，不负责执行能力。
- `input_schema` 使用 JSON Schema 风格字典，便于后续适配本地工具、MCP 工具和技能。
"""

from typing import Any, Literal

from pydantic import BaseModel, Field


CapabilityType = Literal["local_tool", "mcp_tool", "skill", "knowledge_base"]
RiskLevel = Literal["low", "medium", "high"]


class CapabilitySpec(BaseModel):
    """
    Runtime 内部统一使用的能力说明。

    字段说明：
    - name: 全局唯一能力名称，建议使用命名空间格式，例如 `local.calculator`。
    - capability_type: 能力来源类型，用于后续路由和展示。
    - description: 面向 Planner 或 Router 的简短能力描述。
    - input_schema: 执行参数结构，使用 JSON Schema 风格表达。
    - output_schema: 可选输出结构，Phase 1 暂不强制使用。
    - metadata: 扩展元数据，用于保留来源、标签或版本等信息。
    """

    name: str = Field(min_length=1)
    capability_type: CapabilityType
    description: str = Field(min_length=1)
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] | None = None
    risk_level: RiskLevel = "low"
    metadata: dict[str, Any] = Field(default_factory=dict)
