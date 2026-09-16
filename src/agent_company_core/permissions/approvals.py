"""Exact-match human approval contracts."""

import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import UUID, uuid4

from agent_company_core.contracts import RiskLevel


@dataclass(frozen=True, slots=True)
class ApprovalRequest:
    id: UUID
    action: str
    target: str
    arguments: dict[str, object]
    risk: RiskLevel
    requested_by: str
    mission_id: UUID | None
    request_hash: str
    expires_at: datetime

    @classmethod
    def create(
        cls,
        *,
        action: str,
        target: str,
        arguments: dict[str, object],
        risk: RiskLevel,
        requested_by: str,
        mission_id: UUID | None,
        ttl: timedelta = timedelta(hours=1),
    ) -> "ApprovalRequest":
        canonical = json.dumps(
            {"action": action, "target": target, "arguments": arguments},
            sort_keys=True,
            separators=(",", ":"),
        )
        return cls(
            uuid4(),
            action,
            target,
            arguments,
            risk,
            requested_by,
            mission_id,
            sha256(canonical.encode()).hexdigest(),
            datetime.now(UTC) + ttl,
        )


@dataclass(frozen=True, slots=True)
class ApprovalResolution:
    approved: bool
    resolved_by: str
    request_hash: str
    modified_arguments: dict[str, object] | None = None


def is_exact_match(
    request: ApprovalRequest, resolution: ApprovalResolution, *, now: datetime | None = None
) -> bool:
    if request.request_hash != resolution.request_hash:
        return False
    if (now or datetime.now(UTC)) >= request.expires_at:
        return False
    if resolution.modified_arguments is not None:
        canonical = json.dumps(
            {
                "action": request.action,
                "target": request.target,
                "arguments": resolution.modified_arguments,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return sha256(canonical.encode()).hexdigest() == request.request_hash
    return True
