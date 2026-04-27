import asyncio
from pathlib import Path

import pytest

from agent_runtime_lab.tools.calculator import CalculatorCapability, CalculatorError
from agent_runtime_lab.tools.file_tools import FileReadCapability, FileToolError


def test_calculator_executes_basic_arithmetic() -> None:
    calculator = CalculatorCapability()

    result = asyncio.run(calculator.arun({"expression": "1 + 2 * 3"}, context={}))

    assert result == 7


def test_calculator_respects_parentheses_and_unary_operators() -> None:
    calculator = CalculatorCapability()

    result = asyncio.run(calculator.arun({"expression": "-(2 + 3) * 4"}, context={}))

    assert result == -20


def test_calculator_supports_float_division() -> None:
    calculator = CalculatorCapability()

    result = asyncio.run(calculator.arun({"expression": "7 / 2"}, context={}))

    assert result == 3.5


def test_calculator_rejects_missing_expression() -> None:
    calculator = CalculatorCapability()

    with pytest.raises(CalculatorError, match="expression"):
        asyncio.run(calculator.arun({}, context={}))


def test_calculator_rejects_function_calls() -> None:
    calculator = CalculatorCapability()

    with pytest.raises(CalculatorError, match="Unsupported expression node"):
        asyncio.run(calculator.arun({"expression": "__import__('os').system('dir')"}, context={}))


def test_calculator_rejects_names() -> None:
    calculator = CalculatorCapability()

    with pytest.raises(CalculatorError, match="Unsupported expression node"):
        asyncio.run(calculator.arun({"expression": "price + 1"}, context={}))


def test_calculator_spec_uses_capability_contract() -> None:
    spec = CalculatorCapability().spec()

    assert spec.name == "local.calculator"
    assert spec.capability_type == "local_tool"
    assert spec.input_schema["required"] == ["expression"]


def test_file_read_reads_workspace_text_file(workspace_tmp: Path) -> None:
    workspace = workspace_tmp / "workspace"
    workspace.mkdir()
    target_file = workspace / "notes.txt"
    target_file.write_text("hello runtime", encoding="utf-8")
    file_read = FileReadCapability(workspace)

    result = asyncio.run(file_read.arun({"path": "notes.txt"}, context={}))

    assert result == "hello runtime"


def test_file_read_rejects_absolute_path(workspace_tmp: Path) -> None:
    workspace = workspace_tmp / "workspace"
    workspace.mkdir()
    outside_file = workspace_tmp / "outside.txt"
    outside_file.write_text("secret", encoding="utf-8")
    file_read = FileReadCapability(workspace)

    with pytest.raises(FileToolError, match="Absolute paths"):
        asyncio.run(file_read.arun({"path": str(outside_file)}, context={}))


def test_file_read_rejects_workspace_escape(workspace_tmp: Path) -> None:
    workspace = workspace_tmp / "workspace"
    workspace.mkdir()
    outside_file = workspace_tmp / "outside.txt"
    outside_file.write_text("secret", encoding="utf-8")
    file_read = FileReadCapability(workspace)

    with pytest.raises(FileToolError, match="escapes workspace"):
        asyncio.run(file_read.arun({"path": "../outside.txt"}, context={}))


def test_file_read_rejects_missing_path(workspace_tmp: Path) -> None:
    file_read = FileReadCapability(workspace_tmp)

    with pytest.raises(FileToolError, match="path"):
        asyncio.run(file_read.arun({}, context={}))


def test_file_read_spec_uses_capability_contract(workspace_tmp: Path) -> None:
    spec = FileReadCapability(workspace_tmp).spec()

    assert spec.name == "local.file_read"
    assert spec.capability_type == "local_tool"
    assert spec.input_schema["required"] == ["path"]
