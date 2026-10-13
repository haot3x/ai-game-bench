from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest


@pytest.fixture
def dom_task() -> Path:
    default = (
        Path(__file__).parent.parent / "datasets/smoke-create-v0.2" / "create-click-counter-zh-001"
    )
    return Path(os.environ.get("GAMEBENCH_DOM_TASK", default))


@pytest.fixture
def dom_verifier(dom_task: Path):
    spec = importlib.util.spec_from_file_location(
        "dom_verifier", dom_task / "tests/verify_submission.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
