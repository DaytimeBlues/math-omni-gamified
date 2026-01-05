import asyncio
import os

async def some_async_op(val):
    await asyncio.sleep(0.01)
    return val * 2

def demonstrate_problem():
    print("DEMO: The _run() pattern")
    def _run(coro):
        return asyncio.run(coro)

    # This works in isolated snippets but fails if state is shared across calls
    res1 = _run(some_async_op(5))
    res2 = _run(some_async_op(10))
    print(f"Results: {res1}, {res2}")
    print("Status: Dangerous if objects (like DB connections) are kept between calls.")

if __name__ == "__main__":
    demonstrate_problem()
