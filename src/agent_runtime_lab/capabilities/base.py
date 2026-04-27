"""
Capability 抽象基类。

模块职责：
1. 定义所有能力实现必须遵守的最小接口。
2. 让 Runtime 通过统一方式获取能力说明并执行能力。
3. 隔离不同能力来源的内部实现细节。

设计说明：
- Runtime 只依赖 `BaseCapability`，不直接依赖具体工具或 MCP SDK 对象。
- 具体能力负责校验和解释自身参数。
"""

from abc import ABC, abstractmethod
from typing import Any

from agent_runtime_lab.schemas.capability import CapabilitySpec


class BaseCapability(ABC):
    """
    Runtime 可执行能力的统一接口。

    实现约束：
    - `spec()` 必须返回稳定的能力说明。
    - `arun()` 必须是异步接口，便于后续统一接入网络工具、MCP 和 LLM 调用。
    """

    @abstractmethod
    def spec(self) -> CapabilitySpec:
        """返回能力说明。"""

    @abstractmethod
    async def arun(self, arguments: dict[str, Any], context: dict[str, Any]) -> Any:
        """执行能力并返回原始结果。"""

    @property
    def name(self) -> str:
        """返回能力名称，方便注册表和调试代码使用。"""

        return self.spec().name
