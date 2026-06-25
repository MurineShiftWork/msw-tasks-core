"""
Test protocol: reward port wiring check.

Lights up reward ports one at a time, in order. Bpod waits for the IR beam
break (poke) on the lit port before advancing to the next, and fires a TTL
pulse on each port transition so wiring/timing can be verified externally
(scope, ephys digital-in, etc).

Per port: led_on (wait for PortNIn) -> ttl_on -> ttl_off (LED off) -> exit.
"""

import logging
import time

from murineshiftwork.hardware.bpod.ttl import add_trial_onset_ttl
from murineshiftwork.logic.task_process import TaskProcess, TaskRunner
from pybpodapi.protocol import Bpod
from pybpodapi.state_machine import StateMachine

_DEFAULTS = {
    "PORTS": [1, 2, 3, 4, 5, 6, 7, 8],
    "PWM_INTENSITY": 255,
    "TTL_BNC_CHANNEL": 1,
    "TTL_PULSE_DURATION_S": 0.01,
}


class Task(TaskRunner):
    def run(self) -> None:
        s = {**_DEFAULTS, **self.input_kwargs.get("settings.task.patched", {})}

        ports = list(s["PORTS"])
        pwm_intensity = int(s["PWM_INTENSITY"])
        ttl_pulse_duration_s = float(s["TTL_PULSE_DURATION_S"])
        bnc_channel = f"BNC{int(s['TTL_BNC_CHANNEL'])}"

        logging.info(
            f"Bpod wiring check: ports={ports} | pwm={pwm_intensity} | "
            f"ttl={bnc_channel} ({ttl_pulse_duration_s * 1000:.0f}ms)"
        )

        for port in ports:
            if not self.continue_task:
                break

            logging.info(f"Port {port}: lighting LED, waiting for poke...")

            poke_in_event = getattr(Bpod.Events, f"Port{port}In")

            sma = StateMachine(bpod=self.bpod)
            sma.add_state(
                state_name="led_on",
                state_timer=0,
                state_change_conditions={poke_in_event: "ttl_on"},
                output_actions=[(f"PWM{port}", pwm_intensity)],
            )
            sma = add_trial_onset_ttl(
                sma=sma,
                state_name_tuple=("ttl_on", "ttl_off"),
                ttl_pulse_duration=ttl_pulse_duration_s,
                bnc_channel=bnc_channel,
                next_state="led_off",
            )
            sma.add_state(
                state_name="led_off",
                state_timer=0,
                state_change_conditions={Bpod.Events.Tup: "exit"},
                output_actions=[(f"PWM{port}", 0)],
            )

            self.bpod.send_state_machine(sma)
            if not self.bpod.run_state_machine(sma):
                logging.warning(f"No data returned from state machine on port {port}.")

            logging.info(f"Port {port}: poke detected, TTL pulse sent.")

        logging.info("Bpod wiring check complete.")


def run_task(**kwargs):
    with TaskProcess(**kwargs) as tp:
        while tp.is_running():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                tp.stop_task()


if __name__ == "__main__":
    print("main")
