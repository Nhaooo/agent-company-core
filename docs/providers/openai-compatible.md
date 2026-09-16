# OpenAI-compatible endpoints

Install the optional SDK extra:

```powershell
python -m pip install "agent-company-core[openai]"
$env:OPENAI_API_KEY = "..."
$env:OPENAI_BASE_URL = "https://api.example.test/v1"
$env:OPENAI_MODEL = "your-model-id"
```

`OpenAICompatibleModel` uses the official async OpenAI client and the common
`chat.completions` contract. `OPENAI_BASE_URL` is optional for the hosted
default and useful for gateways or local servers. The model identifier is
always configurable.

```python
from agent_company_core import OpenAICompatibleModel

model = OpenAICompatibleModel(
    model=os.environ["OPENAI_MODEL"],
    base_url=os.environ.get("OPENAI_BASE_URL"),
)
```

When a typed response is requested, the adapter asks for a JSON object and
validates it with the supplied Pydantic schema. Compatible servers vary in
their structured-output support; keep a fallback provider and test the exact
endpoint you deploy.

No real key appears in this repository. The tests inject a fake async client.
