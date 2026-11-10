"""stage_move never opens the real stage in a simulated run."""

from __future__ import annotations

import pytest

pytest.importorskip("murineshiftwork.tasks._test_stage_move.task")

from murineshiftwork.tasks._test_stage_move import task as stage_move  # noqa: E402


def test_simulated_run_does_not_open_the_stage(monkeypatch):
    def _refuse(*args, **kwargs):
        raise AssertionError("real stage opened in a simulated run")

    monkeypatch.setattr(stage_move.StageController, "from_config", _refuse)
    t = stage_move.Task.__new__(stage_move.Task)
    t.input_kwargs = {
        "simulate": True,
        "settings.task.patched": {
            "serial_port_stage": "COM9",
            "settings.stage": {"axes": {"x": {}}},
        },
    }
    t.run()
