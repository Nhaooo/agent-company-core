# FastAPI

The optional reference app exposes health, chat, mission, tool, memory, and
STOP endpoints. Install the app extra and run it locally:

```powershell
python -m pip install "agent-company-core[app]"
agent-company-reference
```

The app uses `FakeModel` and binds to localhost by default. It is a development
reference, not a production deployment. Add authentication, authorization,
rate limits, durable operational controls, and a deployment threat model for a
real service.
