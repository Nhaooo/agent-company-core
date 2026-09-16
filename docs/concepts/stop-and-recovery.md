# STOP and recovery

`StopControl` persists an operator signal in `stop.json`. The engine checks it
before model work, before tool work, and after a tool returns. A mission that
observes the signal becomes `stopped`; a request already sent to an external
provider cannot be recalled.

After the operator clears the signal, a stopped mission can be queued again by
the application and resumed according to its checkpoint and recovery policy.
The control is a local coordination boundary, not a distributed cancellation
guarantee.
