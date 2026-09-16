# Human approval

High-risk actions and configured sensitive action names produce an exact-match
`ApprovalRequest`. The request hash covers the action, target, and arguments.
An approval cannot be reused for modified arguments or after its expiry.

```python
waiting = await engine.run_mission(mission.id)
approval = engine.store.list_approvals(mission.id)[0]
# Show the request to an authenticated operator, then resolve its exact hash.
```

Application owners remain responsible for authenticating the operator and for
deciding which human is allowed to approve which effect.
