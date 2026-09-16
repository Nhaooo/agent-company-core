# Human approval

Demonstrates a high-risk registered tool pausing a durable mission until an
operator resolves the exact request hash.

Prerequisites: core package. Run `python examples/human_approval/main.py`.
Expected behavior: the mission waits for approval, then executes the harmless
staging action after an exact approval.
