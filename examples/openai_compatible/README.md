# OpenAI-compatible provider

Demonstrates the generic optional adapter with a mocked chat-completions client
by default. It can target OpenAI, a gateway, or another compatible endpoint.

Prerequisites: core package for the default run. For a live call, install
`agent-company-core[openai]`, configure `OPENAI_API_KEY`, optionally set
`OPENAI_BASE_URL` and `OPENAI_MODEL`, then pass `--live`.

```powershell
python examples/openai_compatible/main.py
python examples/openai_compatible/main.py --live
```

The example uses `gpt-5.6-terra` as an illustrative current model ID only; use
the model catalog for the endpoint you actually operate.
