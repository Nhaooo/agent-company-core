# Memory

`MemoryStore` separates memory operations from mission orchestration. The
default `SQLiteMemoryStore` persists scoped `MemoryItem` values in the same
local SQLite file and supports simple text search.

Memory is application data. Define retention, access control, and redaction
policies before storing sensitive content.
