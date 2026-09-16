# Research team

Demonstrates a small durable team made from neutral planner, researcher, and
reviewer agents. Each role gets a separate mission with explicit capability
delegation; the fake provider keeps the example deterministic.

Prerequisites: core package. Run `python examples/research_team/main.py`.
Expected behavior: all three missions complete, and the reopened SQLite store
shows durable completed state and audit events.
