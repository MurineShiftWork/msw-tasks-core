# msw-tasks-core

Core task set for [Murine Shift Work](https://github.com/MurineShiftWork/murineshiftwork):
liquid and sound calibration protocols, plus minimal hardware test tasks.

Installs as a namespace contributor to `murineshiftwork.tasks.*`.
Tasks are discoverable by the `msw` CLI via both namespace path scan and `msw.tasks` entry points.

## Installation

```bash
pip install msw-tasks-core
```

Requires `murineshiftwork` to be installed.

## Tasks included

**Calibration**
- `_calibration_liquid_dynamic` - dynamic liquid volume calibration
- `_calibration_liquid_static` - static liquid volume calibration
- `_calibration_sound_latency` - sound output latency measurement

**Hardware tests**
- `_test_bpod_connect` - verify Bpod serial connection
- `_test_flush_valves` - flush all Bpod valve ports
- `_test_minimal_task` - minimal state-machine smoke test
- `_test_pulsepal_connect` - verify PulsePal connection
- `_test_stage_move` - exercise one-axis stage movement
- `_test_ttl_barcodes` - TTL barcode encoding/decoding test
- `_test_ttl_outputs` - BNC TTL output test
- `_test_barcode_iti` - barcode-in-ITI timing test
- `_test_video` - video acquisition smoke test

## Development

```bash
# from workspace root
uv sync
```
