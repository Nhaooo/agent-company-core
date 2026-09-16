# Ollama and local models

Ollama exposes an OpenAI-compatible endpoint. Install the generic adapter, run
Ollama locally, and configure the endpoint without adding an Ollama runtime
dependency:

```powershell
python -m pip install "agent-company-core[openai]"
$env:OLLAMA_BASE_URL = "http://127.0.0.1:11434/v1"
$env:OLLAMA_MODEL = "llama3.2"
```

```python
import os

from agent_company_core import OpenAICompatibleModel

model = OpenAICompatibleModel(
    model=os.environ.get("OLLAMA_MODEL", "llama3.2"),
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1"),
    api_key=os.environ.get("OLLAMA_API_KEY", "ollama"),
)
```

The default `ollama` value is a local placeholder, not a credential. The
repository example uses a mocked client unless `--live` is explicitly passed,
so an absent Ollama installation does not fail the test suite.
