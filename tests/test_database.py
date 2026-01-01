# tests/test_database.py
"""Tests for the Database Service."""
import os
import asyncio
import pytest
from core.database import DatabaseService

TEST_DB_PATH = "data/test_math_omni.db"


def _run(coro):
    """Run a coroutine to completion using asyncio.run."""
    return asyncio.run(coro)


@pytest.fixture
def db():
    """Create a fresh test database."""
    service = DatabaseService()
    service.db_path = TEST_DB_PATH

    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    _run(service.initialize())
    yield service
    _run(service.close())

    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


def test_initial_egg_balance_is_zero(db: DatabaseService):
    """New users should start with 0 eggs."""
    eggs = _run(db.get_eggs())
    assert eggs == 0


def test_add_eggs_increases_balance(db: DatabaseService):
    """Adding eggs should increase the balance."""
    initial = _run(db.get_eggs())
    new_total = _run(db.add_eggs(10))

    assert new_total == initial + 10
    assert _run(db.get_eggs()) == new_total


def test_add_eggs_multiple_times(db: DatabaseService):
    """Multiple additions should accumulate correctly."""
    _run(db.add_eggs(5))
    _run(db.add_eggs(10))
    total = _run(db.add_eggs(3))

    assert total == 18


def test_initial_unlocked_level_is_one(db: DatabaseService):
    """New users should have level 1 unlocked by default."""
    unlocked = _run(db.get_unlocked_level())
    assert unlocked == 1


def test_unlock_level_advances_progress(db: DatabaseService):
    """Completing a level should unlock the next one."""
    _run(db.unlock_level(1))
    unlocked = _run(db.get_unlocked_level())
    assert unlocked == 2


def test_unlock_multiple_levels(db: DatabaseService):
    """Completing multiple levels should work correctly."""
    _run(db.unlock_level(1))
    _run(db.unlock_level(2))
    _run(db.unlock_level(3))

    unlocked = _run(db.get_unlocked_level())
    assert unlocked == 4


def test_unlock_level_is_idempotent(db: DatabaseService):
    """Unlocking the same level twice shouldn't cause issues."""
    _run(db.unlock_level(1))
    _run(db.unlock_level(1))

    unlocked = _run(db.get_unlocked_level())
    assert unlocked == 2


def test_close_and_reopen_preserves_data(db: DatabaseService):
    """Data should persist after closing and reopening."""
    _run(db.add_eggs(100))
    _run(db.unlock_level(5))
    _run(db.close())

    # Reopen
    db2 = DatabaseService()
    db2.db_path = TEST_DB_PATH
    _run(db2.initialize())

    assert _run(db2.get_eggs()) == 100
    assert _run(db2.get_unlocked_level()) == 6

    _run(db2.close())
