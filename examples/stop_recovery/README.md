# STOP and recovery

Demonstrates a persistent operator STOP, a stopped mission, and an explicit
resume after the signal is cleared.

Prerequisites: core package. Run `python examples/stop_recovery/main.py`.
Expected behavior: the first run is stopped before model work; the resumed run
completes with the offline FakeModel.
