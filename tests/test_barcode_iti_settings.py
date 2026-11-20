"""The task.yaml defaults of the barcode test task use only keys the task reads."""

from pathlib import Path

import pytest
import yaml

pytest.importorskip("pybpodapi")

from murineshiftwork.tasks._test_barcode_iti import task as mod  # noqa: E402


def test_task_yaml_keys_match_code_defaults():
    raw = yaml.safe_load((Path(mod.__file__).parent / "task.yaml").read_text())
    assert set(raw["default"]) <= set(mod._DEFAULTS)


class _Writer:
    def __init__(self):
        self.trials = []

    def write_trial(self, trial):
        self.trials.append(trial)


def test_runs_on_the_simulated_bpod_and_emits_every_trial():
    from murineshiftwork.hardware.bpod.sim import SimBpod

    bpod = SimBpod()
    bpod.open()
    writer = _Writer()
    settings = {"n_max_trials": 3, "inter_trial_interval": 0.1, "wait_duration": 0}
    mod.Task(
        bpod=bpod, trial_writer=writer, **{"settings.task.patched": settings}
    ).run()
    assert [t["info"]["trial_index"] for t in writer.trials] == [0, 1, 2]
    assert all(t["info"]["barcode_value"] is not None for t in writer.trials)
