"""
Async Database Service - Egg Economy Persistence

Uses aiosqlite for non-blocking database operations.

FIXES APPLIED (AI Review):
- Added close() method for lifecycle management (ChatGPT)
- Added busy_timeout and retry logic for locked database (ChatGPT 5.2)
- Added write lock to serialize concurrent writes (ChatGPT 5.2)
"""

import asyncio
import logging
import sqlite3
from typing import Optional, Callable, TypeVar
import aiosqlite
import os

logger = logging.getLogger(__name__)

DB_PATH = os.path.join("data", "math_omni.db")

T = TypeVar('T')


class DatabaseService:
    """Async database for the egg economy and progress tracking."""
    
    def __init__(self):
        self.db_path = DB_PATH
        self._connection: Optional[aiosqlite.Connection] = None
        self._write_lock = asyncio.Lock()  # ChatGPT 5.2 Fix: Serialize writes
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    async def _ensure_connected(self) -> aiosqlite.Connection:
        """
        Ensure we have a persistent connection with proper pragmas.

        ChatGPT 5.2 Fix: Added busy_timeout to handle locked database.
        Code Review Fix: Added error handling for connection failures.
        """
        if self._connection is not None:
            return self._connection

        try:
            conn = await aiosqlite.connect(self.db_path, timeout=5.0)
            # ChatGPT 5.2 Fix: Wait up to 5s for locks instead of failing immediately
            await conn.execute("PRAGMA busy_timeout=5000;")
            await conn.execute("PRAGMA journal_mode=WAL;")
            await conn.execute("PRAGMA synchronous=NORMAL;")
            await conn.execute("PRAGMA foreign_keys=ON;")
            self._connection = conn
            return conn
        except sqlite3.OperationalError as e:
            logger.error("Database connection failed: %s", e)
            raise
        except PermissionError as e:
            logger.error("Database permission denied: %s", e)
            raise
        except Exception as e:
            logger.error("Unexpected database error: %s", e)
            raise

    async def _retry_locked(self, fn: Callable, *, retries: int = 3, base_delay: float = 0.2, timeout: float = 10.0) -> T:
        """
        ChatGPT 5.2 Fix: Retry logic for database locked/busy errors.
        z.ai Fix: Added timeout to prevent hanging forever.
        
        Handles antivirus scans, backup sync, or indexing touching the DB file.
        """
        for i in range(retries):
            try:
                # z.ai Fix: Wrap in timeout to prevent infinite hang
                return await asyncio.wait_for(fn(), timeout=timeout)
            except asyncio.TimeoutError:
                logger.error("Database operation timed out after %.1fs", timeout)
                raise
            except sqlite3.OperationalError as e:
                msg = str(e).lower()
                if "locked" not in msg and "busy" not in msg:
                    raise
                logger.warning("Database locked, retrying in %.1fs (attempt %d/%d)", 
                               base_delay * (2 ** i), i + 1, retries)
                await asyncio.sleep(base_delay * (2 ** i))
        # Last attempt (let it raise so caller can show "Oops" once)
        return await asyncio.wait_for(fn(), timeout=timeout)

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
        """
        Add eggs and return new total.
        
        ChatGPT 5.2 Fix: Serialized with write lock and retry logic.
        """
        db = await self._ensure_connected()
        
        async with self._write_lock:
            async def op():
                # Ensure wallet row exists even if DB file was replaced/corrupted
                await db.execute("INSERT OR IGNORE INTO economy (id, balance) VALUES (1, 0)")
                await db.execute("UPDATE economy SET balance = balance + ? WHERE id=1", (amount,))
                cursor = await db.execute("SELECT balance FROM economy WHERE id=1")
                try:
                    row = await cursor.fetchone()
                finally:
                    await cursor.close()
                await db.commit()
                return row[0] if row else 0

            try:
                return await self._retry_locked(op)
            except Exception:
                # Child-safe: don't crash callers; return a safe default and log
                logger.exception("add_eggs failed")
                return 0

    async def unlock_level(self, level_id: int):
        """
        Mark a level as completed.
        
        ChatGPT 5.2 Fix: Serialized with write lock.
        """
        db = await self._ensure_connected()
        
        async with self._write_lock:
            async def op():
                await db.execute("""
                    INSERT OR REPLACE INTO progress (level_id, completed) 
                    VALUES (?, 1)
                """, (level_id,))
                await db.commit()
            
            try:
                await self._retry_locked(op)
            except Exception:
                logger.exception("unlock_level failed for level %d", level_id)
    
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
        """Close database connection."""
        if self._connection is None:
            return
        try:
            await self._connection.close()
        finally:
            self._connection = None
