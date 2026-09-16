"""Persistence interfaces and local implementation."""

from .sqlite import SQLiteStore

__all__ = ["SQLiteStore"]
