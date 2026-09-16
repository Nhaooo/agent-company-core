# Decisions

Models return an `AgentDecision`, not an application-side effect. Actions are
typed as `respond`, `delegate`, `create_mission`, `use_tool`,
`request_approval`, or `wait`.

When a provider returns structured JSON, the adapter validates it with the
requested Pydantic schema. A plain text provider response is represented as a
typed `respond` decision. The engine then applies policy, STOP, persistence,
and audit controls.
