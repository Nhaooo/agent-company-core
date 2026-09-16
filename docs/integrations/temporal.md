# Temporal

The optional `connect_temporal` helper is a client gateway for a host-owned
Temporal workflow:

```powershell
python -m pip install "agent-company-core[temporal]"
```

Workflow definitions remain in the application so the host can preserve
Temporal's deterministic replay rules. The compact local `MissionEngine` does
not claim Temporal's workflow durability guarantees.
