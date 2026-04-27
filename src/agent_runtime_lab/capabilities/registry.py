"""
Capability 注册表。

模块职责：
1. 保存当前 Runtime 可用的能力实例。
2. 按名称解析能力，供 Router 或 Runtime 执行。
3. 向 Planner 或 Router 暴露能力说明列表。

设计说明：
- 注册表不负责选择能力，只负责存储和解析能力。
- 重复注册默认视为配置错误，避免后续路由结果不确定。
"""

from collections.abc import Iterable

from agent_runtime_lab.capabilities.base import BaseCapability
from agent_runtime_lab.schemas.capability import CapabilitySpec


class CapabilityRegistryError(Exception):
    """Capability 注册表基础异常。"""


class DuplicateCapabilityError(CapabilityRegistryError):
    """能力名称重复时抛出的异常。"""


class CapabilityNotFoundError(CapabilityRegistryError):
    """能力不存在时抛出的异常。"""


class CapabilityRegistry:
    """
    Runtime 使用的能力注册表。

    当前限制：
    - Phase 1 仅支持进程内注册。
    - 后续 MCP、Skill 和 Knowledge Base 可以通过 adapter 注册为统一能力。
    """

    def __init__(self, capabilities: Iterable[BaseCapability] | None = None) -> None:
        self._capabilities: dict[str, BaseCapability] = {}

        if capabilities is not None:
            for capability in capabilities:
                self.register(capability)

    def register(self, capability: BaseCapability, *, replace: bool = False) -> None:
        """
        注册一个能力实例。

        参数说明：
        - capability: 待注册能力。
        - replace: 是否允许覆盖已有同名能力。
        """

        name = capability.spec().name
        if name in self._capabilities and not replace:
            raise DuplicateCapabilityError(f"Capability already registered: {name}")

        self._capabilities[name] = capability

    def get(self, name: str) -> BaseCapability:
        """按名称获取能力实例。"""

        try:
            return self._capabilities[name]
        except KeyError as exc:
            raise CapabilityNotFoundError(f"Capability not found: {name}") from exc

    def list_specs(self) -> list[CapabilitySpec]:
        """按注册顺序返回所有能力说明。"""

        return [capability.spec() for capability in self._capabilities.values()]

    def names(self) -> list[str]:
        """按注册顺序返回所有能力名称。"""

        return list(self._capabilities)

    def __contains__(self, name: object) -> bool:
        return name in self._capabilities

    def __len__(self) -> int:
        return len(self._capabilities)
