# Missions

`MissionCreate` describes an objective. `MissionEngine.create_mission` stores
it in SQLite and emits an audit event. `run_mission` moves it through queued
and running states before applying a validated decision.

Mission state includes:

- status and append-only events;
- assigned agent IDs;
- an optional checkpoint;
- an optional idempotency key;
- timestamps and a priority.

`SQLiteStore` is the small local implementation. The interface is intentionally
replaceable; PostgreSQL and Temporal integrations are not silently substituted
for the local store.
