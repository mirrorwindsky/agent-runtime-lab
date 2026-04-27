"""
本地能力 Runtime 最小演示。

运行方式：
python examples/calculator_demo.py
"""

import asyncio
from pathlib import Path

from agent_runtime_lab.capabilities.registry import CapabilityRegistry
from agent_runtime_lab.runtime.runtime import AgentRuntime
from agent_runtime_lab.tools.calculator import CalculatorCapability
from agent_runtime_lab.tools.file_tools import FileReadCapability


async def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    registry = CapabilityRegistry(
        [
            CalculatorCapability(),
            FileReadCapability(project_root),
        ]
    )
    runtime = AgentRuntime(registry)

    calculator_result = await runtime.arun("calculate 1 + 2 * (3 + 4)")
    readme_result = await runtime.arun("read README.md")

    print(f"Calculator result: {calculator_result.final_response}")
    print(f"README preview: {readme_result.final_response[:80]}")


if __name__ == "__main__":
    asyncio.run(main())
