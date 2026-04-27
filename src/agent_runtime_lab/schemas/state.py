"""
Agent runtime 状态结构。

模块职责：
1. 定义 Runtime 单次执行返回给调用方的结果结构。
2. 保留 action 和 observation，便于测试、调试和后续追踪。
3. 为后续会话状态扩展提供基础模型。
"""

from pydantic import BaseModel

from agent_runtime_lab.schemas.action import AgentAction
from agent_runtime_lab.schemas.observation import Observation


class AgentResult(BaseModel):
    """
    Runtime 单次执行结果。

    字段说明：
    - final_response: 面向调用方的最终响应文本。
    - action: 本次执行选择的能力调用。
    - observation: 能力执行后的结构化观察结果。
    """

    final_response: str
    action: AgentAction
    observation: Observation
