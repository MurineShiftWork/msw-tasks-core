"""Every task in the package runs to completion on the simulated Bpod and devices.

The tasks are found by scanning the package, so a new task is covered without editing this
file. Each task runs through the real ``msw run --simulate`` path in a subprocess with a
scratch home and output directory, so a task that fails on import, on a settings key or on a
device attribute fails here instead of at the rig.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

import murineshiftwork.tasks as tasks_pkg

#: Tasks that measure real hardware and have no simulated counterpart. Keep the reason
#: specific; a task leaves this table as soon as it can run on the simulator.
NOT_SIMULATABLE = {
    "_calibration_sound_latency": "measures the sound card output through a Bpod BNC loopback",
    "_test_video": "drives a network of camera hosts through the camera ensemble conductor",
}

_RUN = "from murineshiftwork.cli import run_cli; run_cli()"
_TIMEOUT_S = 120


def _task_names() -> list[str]:
    names = {
        task_py.parent.name
        for root in tasks_pkg.__path__
        for task_py in Path(root).glob("*/task.py")
    }
    return sorted(names)


@pytest.mark.parametrize("task", _task_names())
def test_task_runs_to_completion_on_the_simulator(task, tmp_path):
    if task in NOT_SIMULATABLE:
        pytest.skip(f"no simulated hardware: {NOT_SIMULATABLE[task]}")

    home = tmp_path / "home"
    home.mkdir()
    env = {
        **os.environ,
        "HOME": str(home),
        "USERPROFILE": str(home),
    }
    env.pop("MSW_CONFIG_DIR", None)

    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            _RUN,
            "run",
            "--simulate",
            "-t",
            task,
            "-s",
            "_test_subject",
            "-o",
            str(tmp_path / "out"),
        ],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        env=env,
        timeout=_TIMEOUT_S,
    )
    assert proc.returncode == 0, proc.stdout[-3000:] + proc.stderr[-3000:]
    assert any((tmp_path / "out").rglob("*")), "the task wrote no session"


def test_exclusions_name_existing_tasks():
    assert set(NOT_SIMULATABLE) <= set(_task_names())
