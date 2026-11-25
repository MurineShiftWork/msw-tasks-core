import time

from murineshiftwork.logic.task_process import TaskProcess, TaskRunner

_MODEL_NAMES = {1: "model-1 (fw<20)", 2: "model-2 (fw>=20)"}


def _info_box(pairs: list[tuple[str, str]]) -> None:
    key_w = max(len(k) for k, _ in pairs)
    lines = [f"{k:<{key_w}} : {v}" for k, v in pairs]
    width = max(len(line) for line in lines)
    bar = "+" + "-" * (width + 4) + "+"
    print(bar)
    for line in lines:
        print(f"|  {line:<{width}}  |")
    print(bar)


class Task(TaskRunner):
    def run(self):
        devices = self.input_kwargs.get("devices") or {}
        handle = devices.get("pulsepal")
        if handle is None:
            raise RuntimeError(
                "PulsePal handle not injected: check setup config has pulsepal device."
            )

        # The simulated PulsePal carries only the attributes tasks need to run, so every
        # field is read with a placeholder instead of failing the diagnostic.
        def read(name, default="n/a"):
            return getattr(handle, name, default)

        model = read("model", None)
        pairs = [
            ("serial port", str(read("serial_port"))),
            ("firmware version", str(read("firmware_version"))),
            ("model", _MODEL_NAMES.get(model, f"unknown ({model})")),
            ("DAC max", str(read("dac_max", None))),
            ("cycle frequency", str(read("cycle_frequency"))),
            ("output channels", str(read("nr_output_channels"))),
            ("trigger channels", str(read("nr_trigger_channels"))),
        ]
        print()
        _info_box(pairs)
        print()


def run_task(**kwargs):
    with TaskProcess(require_bpod=False, **kwargs) as tp:
        while tp.is_running():
            try:
                time.sleep(0.1)
            except KeyboardInterrupt:
                tp.stop_task()


if __name__ == "__main__":
    run_task()
