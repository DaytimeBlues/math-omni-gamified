# tests/test_database.py
"""Tests for the Database Service."""
from __future__ import annotations
import os
import pytest
from core.database import DatabaseService

TEST_DB_PATH = "data/test_math_omni.db"


@pytest.fixture
async def db() -> DatabaseService:
    """Create a fresh test database for each test."""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    service = DatabaseService()
    service.db_path = TEST_DB_PATH
    await service.initialize()
    
    try:
        yield service
    finally:
        await service.close()
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)


@pytest.mark.asyncio
async def test_initial_egg_balance_is_zero(db: DatabaseService):
    """New users should start with 0 eggs."""
    eggs = await db.get_eggs()
    assert eggs == 0


@pytest.mark.asyncio
async def test_add_eggs_increases_balance(db: DatabaseService):
    """Adding eggs should increase the balance."""
    initial = await db.get_eggs()
    new_total = await db.add_eggs(10)

    assert new_total == initial + 10
    assert await db.get_eggs() == new_total


@pytest.mark.asyncio
async def test_add_eggs_multiple_times(db: DatabaseService):
    """Multiple additions should accumulate correctly."""
    await db.add_eggs(5)
    await db.add_eggs(10)
    total = await db.add_eggs(3)

    assert total == 18


@pytest.mark.asyncio
async def test_initial_unlocked_level_is_one(db: DatabaseService):
    """New users should have level 1 unlocked by default."""
    unlocked = await db.get_unlocked_level()
    assert unlocked == 1


@pytest.mark.asyncio
async def test_unlock_level_advances_progress(db: DatabaseService):
    """Completing a level should unlock the next one."""
    await db.unlock_level(1)
    unlocked = await db.get_unlocked_level()
    assert unlocked == 2


@pytest.mark.asyncio
async def test_unlock_multiple_levels(db: DatabaseService):
    """Completing multiple levels should work correctly."""
    await db.unlock_level(1)
    await db.unlock_level(2)
    await db.unlock_level(3)

    unlocked = await db.get_unlocked_level()
    assert unlocked == 4


@pytest.mark.asyncio
async def test_unlock_level_is_idempotent(db: DatabaseService):
    """Unlocking the same level twice shouldn't cause issues."""
    await db.unlock_level(1)
    await db.unlock_level(1)

    unlocked = await db.get_unlocked_level()
    assert unlocked == 2


@pytest.mark.asyncio
async def test_close_and_reopen_preserves_data(db: DatabaseService):
    """Data should persist after closing and reopening."""
    await db.add_eggs(100)
    await db.unlock_level(5)
    await db.close()

    # Reopen
    db2 = DatabaseService()
    db2.db_path = TEST_DB_PATH
    await db2.initialize()

    try:
        assert await db2.get_eggs() == 100
        assert await db2.get_unlocked_level() == 6
    finally:
        await db2.close()
