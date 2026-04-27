"""
测试夹具配置。

模块职责：
1. 提供仓库内的临时测试目录。
2. 避免依赖系统 temp 目录，降低 Windows 权限差异对测试的影响。
"""

from collections.abc import Iterator
from pathlib import Path
import shutil
import uuid

import pytest


@pytest.fixture
def workspace_tmp() -> Iterator[Path]:
    root = Path(".test_artifacts").resolve()
    path = root / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)

    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
