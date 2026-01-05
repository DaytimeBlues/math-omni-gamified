"""Lightweight local async test utilities.

This is a minimal substitute for pytest-asyncio to avoid external
networked dependencies in this environment. It supports async tests
and fixtures using a shared per-test event loop and registers the
common configuration options used by the real plugin.
"""
from __future__ import annotations

import asyncio
import inspect
from typing import Any, Dict

import pytest

# Re-export fixture decorator for compatibility with test suites.
fixture = pytest.fixture


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addini("asyncio_mode", "asyncio mode placeholder", default="auto")
    parser.addini(
        "asyncio_default_fixture_loop_scope",
        "scope for generated event_loop fixture",
        default="function",
    )


def pytest_configure(config: pytest.Config) -> None:
    # Keep parity with the upstream plugin so pytest doesn't warn about unknown markers.
    config.addinivalue_line("markers", "asyncio: mark test as requiring the asyncio loop")


@pytest.fixture
def event_loop() -> asyncio.AbstractEventLoop:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield loop
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        asyncio.set_event_loop(None)


@pytest.hookimpl(tryfirst=True)
def pytest_fixture_setup(fixturedef: pytest.FixtureDef[Any], request: pytest.FixtureRequest) -> Any | None:
    """
    Handle async fixtures.
    pytest 9+ caches fixture values inside the default implementation, so we must
    populate fixturedef.cached_result to prevent double-execution.
    """
    func = fixturedef.func
    if not (inspect.iscoroutinefunction(func) or inspect.isasyncgenfunction(func)):
        return None

    # Use the shared event_loop fixture
    loop = request.getfixturevalue("event_loop")
    kwargs: Dict[str, Any] = {arg: request.getfixturevalue(arg) for arg in fixturedef.argnames}
    cache_key = fixturedef.cache_key(request)

    try:
        if inspect.iscoroutinefunction(func):
            result = loop.run_until_complete(func(**kwargs))
            fixturedef.cached_result = (result, cache_key, None)
            return result

        # Async generator fixture (yield-style)
        agen = func(**kwargs)
        result = loop.run_until_complete(agen.__anext__())

        def _finalizer() -> None:
            try:
                # Consume remaining items and ensure cleanup
                while True:
                    loop.run_until_complete(agen.__anext__())
            except StopAsyncIteration:
                pass
            except Exception:
                pass

        request.addfinalizer(_finalizer)
        fixturedef.cached_result = (result, cache_key, None)
        return result
    except Exception as e:
        fixturedef.cached_result = (None, cache_key, (e, e.__traceback__))
        raise


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> bool | None:
    testfunction = pyfuncitem.obj
    if inspect.iscoroutinefunction(testfunction):
        loop = pyfuncitem.funcargs.get("event_loop")
        close_loop = False
        if loop is None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            close_loop = True
        try:
            # Only pass fixtures actually requested by the test function.
            argnames = getattr(pyfuncitem, "_fixtureinfo").argnames
            testargs = {name: pyfuncitem.funcargs[name] for name in argnames}
            loop.run_until_complete(testfunction(**testargs))
        except Exception:
            raise
        finally:
            if close_loop:
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()
                asyncio.set_event_loop(None)
        return True
    return None
