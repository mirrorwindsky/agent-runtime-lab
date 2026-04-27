"""
本地文件读取能力。

模块职责：
1. 提供受 workspace 边界保护的文本文件读取能力。
2. 防止默认读取任意系统路径或敏感路径。
3. 作为后续文件类工具和 MCP 文件工具适配的安全基线。

当前限制：
- Phase 1 仅支持 UTF-8 文本读取。
- 不支持写文件、列目录或二进制文件读取。
"""

from pathlib import Path
from typing import Any

from agent_runtime_lab.capabilities.base import BaseCapability
from agent_runtime_lab.schemas.capability import CapabilitySpec


class FileToolError(ValueError):
    """文件工具执行失败时抛出的异常。"""


class FileReadCapability(BaseCapability):
    """受限 workspace 内的文本文件读取能力。"""

    def __init__(self, workspace_dir: str | Path) -> None:
        self._workspace_dir = Path(workspace_dir).resolve()

    def spec(self) -> CapabilitySpec:
        return CapabilitySpec(
            name="local.file_read",
            capability_type="local_tool",
            description="读取 workspace 目录内的 UTF-8 文本文件。",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "相对 workspace 的文件路径。",
                    },
                },
                "required": ["path"],
                "additionalProperties": False,
            },
            output_schema={
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                },
                "required": ["content"],
            },
            risk_level="medium",
            metadata={"workspace_dir": str(self._workspace_dir)},
        )

    async def arun(self, arguments: dict[str, Any], context: dict[str, Any]) -> str:
        path = arguments.get("path")
        if not isinstance(path, str) or not path.strip():
            raise FileToolError("File read requires a non-empty string argument: path")

        target_path = self._resolve_workspace_path(path)
        if not target_path.exists():
            raise FileToolError(f"File does not exist: {path}")
        if not target_path.is_file():
            raise FileToolError(f"Path is not a file: {path}")

        return target_path.read_text(encoding="utf-8")

    def _resolve_workspace_path(self, path: str) -> Path:
        """解析并校验目标路径必须位于 workspace 内。"""

        raw_path = Path(path)
        if raw_path.is_absolute():
            raise FileToolError("Absolute paths are not allowed")

        target_path = (self._workspace_dir / raw_path).resolve()
        if not target_path.is_relative_to(self._workspace_dir):
            raise FileToolError(f"Path escapes workspace: {path}")

        return target_path
