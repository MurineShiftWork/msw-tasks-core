"""The flush task stops cleanly, with a clear error, when the Bpod stops acknowledging."""

import logging
from unittest.mock import MagicMock, patch

from pybpodapi.exceptions.bpod_error import BpodErrorException

from murineshiftwork.tasks._test_flush_valves.task import Task

SETTINGS = {
    "settings.task.patched": {
        "VALVE_NUMBERS": [1, 3],
        "N_FLUSH_CYCLES": 5,
        "INTER_FLUSH_INTERVAL_S": 0,
        "FLUSH_VALVES_SEQUENTIALLY": True,
    }
}


def _task(fail_on_call):
    bpod = MagicMock()
    calls = {"n": 0}

    def run_state_machine(sma):
        calls["n"] += 1
        if calls["n"] == fail_on_call:
            raise BpodErrorException("not acknowledged", bpod)
        return True

    bpod.run_state_machine.side_effect = run_state_machine
    return Task(bpod=bpod, **SETTINGS), calls


def test_bpod_error_stops_the_task_with_a_message(caplog):
    task, calls = _task(fail_on_call=3)
    with (
        patch("murineshiftwork.tasks._test_flush_valves.task.StateMachine"),
        caplog.at_level(logging.ERROR),
    ):
        task.run()  # no exception escapes
    assert calls["n"] == 3
    assert task.continue_task is False
    assert "cycle 2/5, valves [1]" in caplog.text


def test_all_cycles_run_without_errors():
    task, calls = _task(fail_on_call=0)
    with patch("murineshiftwork.tasks._test_flush_valves.task.StateMachine"):
        task.run()
    assert calls["n"] == 10
