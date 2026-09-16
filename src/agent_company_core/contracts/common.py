"""Shared strict Pydantic primitives."""

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """Base model that rejects unrecognised fields at trust boundaries."""

    model_config = ConfigDict(extra="forbid", frozen=False)
