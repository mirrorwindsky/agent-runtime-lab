from typing import Any

import pytest

from agent_runtime_lab.capabilities.base import BaseCapability
from agent_runtime_lab.capabilities.registry import (
    CapabilityNotFoundError,
    CapabilityRegistry,
    DuplicateCapabilityError,
)
from agent_runtime_lab.schemas.capability import CapabilitySpec


class DummyCapability(BaseCapability):
    def __init__(self, name: str = "local.dummy") -> None:
        self._spec = CapabilitySpec(
            name=name,
            capability_type="local_tool",
            description="用于测试注册表行为的虚拟能力。",
            input_schema={
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                },
            },
        )

    def spec(self) -> CapabilitySpec:
        return self._spec

    async def arun(self, arguments: dict[str, Any], context: dict[str, Any]) -> Any:
        return arguments.get("value")


def test_register_and_get_capability() -> None:
    registry = CapabilityRegistry()
    capability = DummyCapability()

    registry.register(capability)

    assert len(registry) == 1
    assert "local.dummy" in registry
    assert registry.get("local.dummy") is capability


def test_list_specs_returns_registered_capability_specs() -> None:
    registry = CapabilityRegistry()
    registry.register(DummyCapability("local.first"))
    registry.register(DummyCapability("local.second"))

    specs = registry.list_specs()

    assert [spec.name for spec in specs] == ["local.first", "local.second"]
    assert all(spec.capability_type == "local_tool" for spec in specs)


def test_names_returns_registered_capability_names() -> None:
    registry = CapabilityRegistry([DummyCapability("local.first"), DummyCapability("local.second")])

    assert registry.names() == ["local.first", "local.second"]


def test_duplicate_registration_raises_clear_error() -> None:
    registry = CapabilityRegistry()
    registry.register(DummyCapability("local.same"))

    with pytest.raises(DuplicateCapabilityError, match="local.same"):
        registry.register(DummyCapability("local.same"))


def test_register_can_replace_existing_capability_explicitly() -> None:
    registry = CapabilityRegistry()
    old_capability = DummyCapability("local.replaceable")
    new_capability = DummyCapability("local.replaceable")

    registry.register(old_capability)
    registry.register(new_capability, replace=True)

    assert registry.get("local.replaceable") is new_capability


def test_missing_capability_raises_clear_error() -> None:
    registry = CapabilityRegistry()

    with pytest.raises(CapabilityNotFoundError, match="local.missing"):
        registry.get("local.missing")
