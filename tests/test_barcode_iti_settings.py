"""The task.yaml defaults of the barcode test task use only keys the task reads."""

from pathlib import Path

import pytest
import yaml

pytest.importorskip("pybpodapi")

from murineshiftwork.tasks._test_barcode_iti import task as mod  # noqa: E402


def test_task_yaml_keys_match_code_defaults():
    raw = yaml.safe_load((Path(mod.__file__).parent / "task.yaml").read_text())
    assert set(raw["default"]) <= set(mod._DEFAULTS)
