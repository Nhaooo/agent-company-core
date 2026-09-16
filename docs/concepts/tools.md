# Tools

Register a `ToolSpec` with a name, capability set, handler, and risk level.
`ToolRegistry.execute` checks STOP and the structured `Policy` before invoking
the handler. High-risk tools pause for an exact approval instead of running.

Keep handlers narrow and auditable. The core does not infer permissions from
natural-language prompts or select tools from hidden keyword rules.
