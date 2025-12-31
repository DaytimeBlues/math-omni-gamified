"""
Async Database Service - Egg Economy Persistence

Uses aiosqlite for non-blocking database operations.

FIXES APPLIED (AI Review):
- Added close() method for lifecycle management (ChatGPT)
"""

import aiosqlite
import os
from typing import Optional

DB_PATH = os.path.join("data", "math_omni.db")


class DatabaseService:
    """Async database for the egg economy and progress tracking."""
    
    def __init__(self):
        self.db_path = DB_PATH
        self._connection: Optional[aiosqlite.Connection] = None
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    async def _ensure_connected(self) -> aiosqlite.Connection:
        """
        Ensure we have a persistent connection.

        Performance note:
        The old implementation opened a new SQLite connection per query, which
        adds measurable latency on spinning disks / slow filesystems and causes
        unnecessary OS-level churn. A single long-lived connection is faster
        and plays nicely with the app's lifecycle-managed `close()`.
        """
        if self._connection is not None:
            return self._connection

        conn = await aiosqlite.connect(self.db_path)
        # Pragmas: safe defaults for a local single-user app.
        # WAL improves concurrent read/write patterns; NORMAL is fine for games.
        await conn.execute("PRAGMA journal_mode=WAL;")
        await conn.execute("PRAGMA synchronous=NORMAL;")
        await conn.execute("PRAGMA foreign_keys=ON;")
        self._connection = conn
        return conn

    async def initialize(self):
        """Create tables if they don't exist."""
        db = await self._ensure_connected()

        await db.execute("""
            CREATE TABLE IF NOT EXISTS economy (
                id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                level_id INTEGER PRIMARY KEY,
                stars INTEGER DEFAULT 0,
                completed BOOLEAN DEFAULT 0
            )
        """)

        # Init wallet if empty
        cursor = await db.execute("SELECT count(*) FROM economy")
        try:
            count = await cursor.fetchone()
        finally:
            await cursor.close()
        if count and count[0] == 0:
            await db.execute("INSERT INTO economy (id, balance) VALUES (1, 0)")

        await db.commit()

    async def get_eggs(self) -> int:
        """Get current egg balance."""
        db = await self._ensure_connected()
        cursor = await db.execute("SELECT balance FROM economy WHERE id=1")
        try:
            row = await cursor.fetchone()
        finally:
            await cursor.close()
        return row[0] if row else 0

    async def add_eggs(self, amount: int) -> int:
        """Add eggs and return new total."""
        db = await self._ensure_connected()
        await db.execute("UPDATE economy SET balance = balance + ? WHERE id=1", (amount,))

        # Avoid a second connection/query round-trip by reading back on the same connection.
        cursor = await db.execute("SELECT balance FROM economy WHERE id=1")
        try:
            row = await cursor.fetchone()
        finally:
            await cursor.close()

        await db.commit()
        return row[0] if row else 0

    async def unlock_level(self, level_id: int):
        """Mark a level as completed."""
        db = await self._ensure_connected()
        await db.execute("""
            INSERT OR REPLACE INTO progress (level_id, completed) 
            VALUES (?, 1)
        """, (level_id,))
        await db.commit()
    
    async def get_unlocked_level(self) -> int:
        """Returns the maximum unlocked level ID + 1 (next available)."""
        db = await self._ensure_connected()
        cursor = await db.execute("SELECT MAX(level_id) FROM progress WHERE completed=1")
        try:
            row = await cursor.fetchone()
        finally:
            await cursor.close()

        # If level N is done, unlock N+1
        return (row[0] + 1) if row and row[0] else 1
    
    async def close(self) -> None:
        """
        Close database connection.
        FIX: ChatGPT - Lifecycle management for proper shutdown.
        """
        if self._connection is None:
            return
        try:
            await self._connection.close()
        finally:
            self._connection = None
