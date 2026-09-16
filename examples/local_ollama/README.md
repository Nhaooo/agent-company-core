# Local Ollama

Demonstrates the zero-paid-API path through the generic OpenAI-compatible
adapter. No Ollama dependency is added to the package.

Prerequisites: core package for the mocked run. For a live run, install
`agent-company-core[openai]`, install Ollama, pull a model, and set
`OLLAMA_MODEL`/`OLLAMA_BASE_URL` before passing `--live`.

```powershell
python examples/local_ollama/main.py
python examples/local_ollama/main.py --live
```

The default base URL is `http://127.0.0.1:11434/v1`. The default `ollama` API
key is a local placeholder for servers that ignore authorization; it is not a
secret.
