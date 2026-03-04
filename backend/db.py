"""
asyncpg connection pool for Neon Postgres.

Usage:
    await init_pool(dsn)    # call once at startup
    pool = get_pool()       # get active pool
    await close_pool()      # call at shutdown
"""

from __future__ import annotations

import os

import asyncpg

_pool: asyncpg.Pool | None = None


async def init_pool(dsn: str | None = None) -> None:
    """Create the asyncpg connection pool.

    Args:
        dsn: Postgres DSN. Defaults to DATABASE_URL env var.
    """
    global _pool  # noqa: PLW0603
    if _pool is not None:
        return

    connection_string: str = dsn or os.getenv("DATABASE_URL", "")
    if not connection_string:
        raise ValueError("DATABASE_URL environment variable is required")

    _pool = await asyncpg.create_pool(
        connection_string,
        min_size=2,
        max_size=10,
        ssl="require",
    )


async def close_pool() -> None:
    """Close the connection pool gracefully."""
    global _pool  # noqa: PLW0603
    if _pool is not None:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    """Return the active connection pool.

    Raises:
        AssertionError: If pool has not been initialized.
    """
    assert _pool is not None, "Database pool not initialized. Call init_pool() first."
    return _pool
