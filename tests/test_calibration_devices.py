"""Liquid calibration takes the scale from the framework's device collection.

msw-core >= 0.29 no longer passes serial_port_scale to tasks; a task gets a scale only by listing
it in required_devices (matched to the setup's device named ``scale``).
"""

from pathlib import Path

import pytest
import yaml

import murineshiftwork.tasks as tasks_pkg

TASKS = ["_calibration_liquid_static", "_calibration_liquid_dynamic"]


def _task_dir(name: str) -> Path:
    for root in tasks_pkg.__path__:
        if (Path(root) / name).is_dir():
            return Path(root) / name
    raise FileNotFoundError(name)


@pytest.mark.parametrize("task", TASKS)
def test_task_requires_bpod_and_scale(task):
    raw = yaml.safe_load((_task_dir(task) / "task.yaml").read_text())
    assert raw["default"]["required_devices"] == ["bpod", "scale"]


@pytest.mark.parametrize("task", TASKS)
def test_task_no_longer_reads_the_dropped_port(task):
    src = (_task_dir(task) / "task.py").read_text()
    assert "serial_port_scale" not in src
    assert 'get("devices")' in src
