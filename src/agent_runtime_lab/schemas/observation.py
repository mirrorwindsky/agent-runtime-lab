"""
Observation 数据结构。

模块职责：
1. 记录能力执行后的结构化观察结果。
2. 区分成功结果和失败错误，避免 Runtime 使用松散异常文本传递状态。
3. 为后续 trace、memory 和 LLM 反思流程提供统一输入。
"""

from typing import Any

from pydantic import BaseModel, Field


class Observation(BaseModel):
    """
    能力执行结果。

    字段说明：
    - capability_name: 产生该观察结果的能力名称。
    - success: 能力是否执行成功。
    - result: 成功时的原始结果。
    - error: 失败时的错误信息。
    """

    capability_name: str = Field(min_length=1)
    success: bool
    result: Any = None
    error: str | None = None
