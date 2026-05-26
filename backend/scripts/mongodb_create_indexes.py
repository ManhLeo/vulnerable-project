#!/usr/bin/env python
"""Create MongoDB indexes for the scans collection.

Usage (from backend/):
    python scripts/mongodb_create_indexes.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.core.database import database_manager  # noqa: E402


async def main() -> None:
    await database_manager.connect()
    await database_manager.ensure_indexes()
    await database_manager.disconnect()
    print("MongoDB indexes created successfully for collection 'scans'.")


if __name__ == "__main__":
    asyncio.run(main())
