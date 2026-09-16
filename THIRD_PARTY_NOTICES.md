# Third-party notices

No third-party source code is copied into this repository. Original source is
licensed under Apache License 2.0.

Runtime dependencies retain their own licenses. The core requires Pydantic;
optional extras include FastAPI/Uvicorn, Google Gen AI, Temporal, SQLAlchemy,
and asyncpg. A local `pip-licenses` inspection of the resolved core, dev, app,
Google, Temporal, and Postgres extras found MIT, BSD, Apache-2.0, PSF, MPL-2.0,
and similarly permissive/compatible notices, with no copied third-party source
in this repository. The resolved dependency graph can change over time, so
downstream redistributors must continue to preserve each dependency's notice
and license terms.
