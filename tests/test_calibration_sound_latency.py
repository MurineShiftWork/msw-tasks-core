"""The sound latency task runs without a calibration_file_sound key.

msw-core resolves calibration file paths only for tasks that do not start with ``_calibration``.
"""

from unittest.mock import MagicMock

from murineshiftwork.cli.defaults import DEFAULT_CALIBRATION_FILE_SOUND

from murineshiftwork.tasks._calibration_sound_latency import task as mod


def _run(monkeypatch, input_kwargs):
    calibration = MagicMock()
    monkeypatch.setattr(mod, "StereoSound", MagicMock())
    monkeypatch.setattr(mod, "CalibrationDataSound", calibration)
    t = object.__new__(mod.Task)
    t.__dict__.update(input_kwargs=input_kwargs, bpod=MagicMock(), continue_task=False)
    t.run()
    return calibration


def test_missing_key_uses_the_default_file(monkeypatch):
    calibration = _run(monkeypatch, {})
    calibration.assert_called_once_with(file_path=DEFAULT_CALIBRATION_FILE_SOUND)


def test_given_file_is_used(monkeypatch):
    calibration = _run(monkeypatch, {"calibration_file_sound": "x.csv"})
    calibration.assert_called_once_with(file_path="x.csv")
