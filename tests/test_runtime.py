import asyncio
from pathlib import Path

import pytest

from agent_runtime_lab.capabilities.registry import CapabilityRegistry
from agent_runtime_lab.runtime.planner import RouterError, SimpleRouter
from agent_runtime_lab.runtime.runtime import AgentRuntime
from agent_runtime_lab.tools.calculator import CalculatorCapability
from agent_runtime_lab.tools.file_tools import FileReadCapability


def build_runtime(workspace_dir: Path) -> AgentRuntime:
    registry = CapabilityRegistry(
        [
            CalculatorCapability(),
            FileReadCapability(workspace_dir),
        ]
    )
    return AgentRuntime(registry)


def test_simple_router_routes_calculator_command() -> None:
    action = SimpleRouter().route("calculate 1 + 2")

    assert action.capability_name == "local.calculator"
    assert action.arguments == {"expression": "1 + 2"}


def test_simple_router_routes_file_read_command() -> None:
    action = SimpleRouter().route("read README.md")

    assert action.capability_name == "local.file_read"
    assert action.arguments == {"path": "README.md"}


def test_simple_router_rejects_unsupported_input() -> None:
    with pytest.raises(RouterError, match="Unsupported input"):
        SimpleRouter().route("hello runtime")


def test_runtime_executes_calculator_capability(workspace_tmp: Path) -> None:
    runtime = build_runtime(workspace_tmp)

    result = asyncio.run(runtime.arun("calc 1 + 2 * 3"))

    assert result.final_response == "7"
    assert result.action.capability_name == "local.calculator"
    assert result.observation.success is True
    assert result.observation.result == 7


def test_runtime_executes_file_read_capability(workspace_tmp: Path) -> None:
    target_file = workspace_tmp / "notes.txt"
    target_file.write_text("runtime note", encoding="utf-8")
    runtime = build_runtime(workspace_tmp)

    result = asyncio.run(runtime.arun("read notes.txt"))

    assert result.final_response == "runtime note"
    assert result.action.capability_name == "local.file_read"
    assert result.observation.success is True
    assert result.observation.result == "runtime note"


def test_runtime_wraps_capability_execution_error(workspace_tmp: Path) -> None:
    runtime = build_runtime(workspace_tmp)

    result = asyncio.run(runtime.arun("read missing.txt"))

    assert result.observation.success is False
    assert result.observation.error is not None
    assert "File does not exist" in result.observation.error
