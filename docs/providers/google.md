# Google Gen AI

The existing Google adapter is optional and remains separate from the core:

```powershell
python -m pip install "agent-company-core[google]"
```

`GoogleModel(model=...)` uses the host application's normal Google credential
chain. Credentials must not be committed to source or placed in examples.
The compact adapter supports the provider-neutral `ModelProvider` contract and
does not claim a full production Vertex AI runtime.
