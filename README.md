# Super Mario Kart RL classroom lab

**[Permanent classroom index](https://github.com/sbardacosta-code/super-mario-kart-rl/blob/main/docs/classroom/README.md)**

An English-language, local reinforcement-learning project for studying how an agent learns, stalls, fails, and regresses. Initial task: **Mario, Mario Circuit 1, Time Trial**. First milestone: a valid lap. Next: reliable five-lap race completion.

**Status on September 16, 2026:** the native Apple Silicon software smoke test passes. The Super Mario Kart ROM is missing. Kart controls, saved start, memory mapping, reward, laps, and termination are **not validated**. No Kart training, gameplay samples, or trained checkpoints exist yet. Scripts fail closed until validation is recorded.

## Start here

- [Classroom index and archived sessions](docs/classroom/README.md)
- [Setup and stop/save/resume commands](docs/SETUP.md)
- [Exactly which ROM to supply](docs/ROM.md)
- [Validation checklist and evidence requirements](docs/VALIDATION.md)
- [Evaluation and recording protocol](docs/PROTOCOL.md)
- [Teacher guide and discussion questions](docs/TEACHER_GUIDE.md)
- [Chronological experiment journal](docs/JOURNAL.md)
- [Current compatibility report](sessions/2026-09-16-setup/REPORT.md)
- [Architecture and limitations](docs/DESIGN.md)
- [Publication and checkpoint Releases](docs/PUBLISHING.md)

## Local setup

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m pytest -q
MPLCONFIGDIR=.cache/matplotlib .venv/bin/python -m kart_rl.doctor --output private/doctor-new.json
```

The project was prepared in its own Git repository. The original [Mario teaching project](https://github.com/sbardacosta-code/mario-rl) was inspected read-only and preserved. No paid cloud compute, GPT calls, or remote inference are used in gameplay, training, evaluation, recording, or chart generation.

This is an educational fan project, not affiliated with Nintendo. Game files and save states remain local; supply your own compatible game file. See [provenance](docs/REFERENCES.md) for third-party sources.
