import logging
import time

from murineshiftwork.logic.calibration import CalibrationDataSound
from murineshiftwork.logic.sounds import StereoSound
from murineshiftwork.logic.task_process import TaskProcess, TaskRunner
from pybpodapi.state_machine import StateMachine


class Task(TaskRunner):
    """Measure true bpod-state -> sound-execution latency.

    Wiring: the sound-card output (the stereo channel carrying the blip) is
    connected to Bpod BNC input 1. On each trial the state machine commands the
    blip via SoftCode and waits for its onset to trip ``BNC1High``. Because the
    BNC event is driven by the actual audio output (not a Bpod BNC out->in
    loopback), the recorded time is the real end-to-end latency including the
    OS/sounddevice audio path.
    """

    _sound_input_event = "BNC1High"

    def run(self) -> None:
        self.sound = StereoSound(sound_device=StereoSound.default_sound_device)
        # Open the persistent low-latency stream under test: triggering a sound
        # then only swaps the playback buffer (no per-sound stream open).
        self.sound.setup_sound_device()
        # Short, loud blip: a crisp onset for a clean BNC threshold crossing.
        self.sound_test = self.sound.register_new_sound(
            frequency=5000, duration=0.01, amplitude=0.5, play_blocking=False
        )

        calibration_sound = CalibrationDataSound(
            file_path=self.input_kwargs["calibration_file_sound"]
        )

        self.bpod.softcode_handler_function = self.sound.execute_sound_handler

        trial_index = 0
        n_max_trials = 201
        try:
            while self.continue_task and trial_index <= n_max_trials:
                logging.debug(f"\ntrial {trial_index}")

                sma = StateMachine(bpod=self.bpod)
                # State entry commands the blip; BNC1High marks its real onset,
                # so the event timestamp is the latency we want to measure.
                sma.add_state(
                    state_name="trigger_sound",
                    state_timer=0.5,  # timeout if no onset is detected
                    state_change_conditions={
                        self._sound_input_event: "sound_off",
                        "Tup": "no_sound",
                    },
                    output_actions=[("SoftCode", self.sound_test)],
                )
                sma.add_state(
                    state_name="sound_off",
                    state_timer=0.05,
                    state_change_conditions={"Tup": "iti"},
                    output_actions=[("SoftCode", self.sound.sound_stop_code)],
                )
                sma.add_state(
                    state_name="no_sound",
                    state_timer=0,
                    state_change_conditions={"Tup": "iti"},
                    output_actions=[("SoftCode", self.sound.sound_stop_code)],
                )
                sma.add_state(
                    state_name="iti",
                    state_timer=0.2,
                    state_change_conditions={"Tup": "exit"},
                    output_actions=[],
                )

                self.bpod.send_state_machine(sma)
                if not self.bpod.run_state_machine(sma):
                    logging.warning("nothing returned")

                ev = dict(self.bpod.session.current_trial.export()["Events timestamps"])
                onset = ev.get(self._sound_input_event, -1)
                if onset != -1:
                    calibration_sound += {"trial": trial_index, "delay": onset[0]}
                    logging.info(
                        "Trial %d: sound latency %.4f s", trial_index, onset[0]
                    )
                else:
                    logging.error(
                        "Trial %d: no sound onset on %s "
                        "(check wiring sound-out -> BNC1 in, and signal level)",
                        trial_index,
                        self._sound_input_event,
                    )

                trial_index += 1
        finally:
            self.sound.close()

        # Save new calibration data for sound offset
        calibration_sound.save()
        calibration_sound.save_calibration_plot()


def run_task(**kwargs):
    with TaskProcess(**kwargs) as tp:
        while tp.is_running():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                tp.stop_task()


if __name__ == "__main__":
    print("main")
