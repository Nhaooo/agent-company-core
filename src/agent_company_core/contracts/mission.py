"""Typed mission lifecycle contracts."""

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import Field

from .common import StrictModel


class MissionStatus(StrEnum):
    RECEIVED = "received"
    PLANNED = "planned"
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    PAUSED = "paused"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    STOPPED = "stopped"


TERMINAL_STATUSES = frozenset(
    {MissionStatus.COMPLETED, MissionStatus.FAILED, MissionStatus.CANCELLED, MissionStatus.STOPPED}
)


class Mission(StrictModel):
    id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=1, max_length=300)
    objective: str = Field(min_length=1, max_length=20_000)
    status: MissionStatus = MissionStatus.RECEIVED
    owner: str = Field(default="system", min_length=1, max_length=200)
    assigned_agents: list[str] = Field(default_factory=list, max_length=20)
    priority: int = Field(default=50, ge=0, le=100)
    idempotency_key: str | None = Field(default=None, max_length=200)
    checkpoint: str | None = Field(default=None, max_length=20_000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class MissionEvent(StrictModel):
    id: UUID = Field(default_factory=uuid4)
    mission_id: UUID
    event_type: str = Field(min_length=1, max_length=100)
    payload: dict[str, object] = Field(default_factory=dict)
    sequence: int = Field(ge=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class MissionCreate(StrictModel):
    title: str = Field(min_length=1, max_length=300)
    objective: str = Field(min_length=1, max_length=20_000)
    owner: str = Field(default="system", min_length=1, max_length=200)
    priority: int = Field(default=50, ge=0, le=100)
    idempotency_key: str | None = Field(default=None, max_length=200)


class MissionResult(StrictModel):
    mission_id: UUID
    status: MissionStatus
    summary: str
    selected_agent: str | None = None
    selected_tool: str | None = None
    checkpoint: str | None = None
