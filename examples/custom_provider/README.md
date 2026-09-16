# Custom provider

Demonstrates the smallest provider implementation: an async `complete` method
returning a typed `ModelResponse`.

Prerequisites: core package. Run `python examples/custom_provider/main.py`.
Expected behavior: the custom provider supplies a deterministic typed response
to the durable engine.
