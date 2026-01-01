"""
Core Utilities
"""
import asyncio
import traceback

import logging


logger = logging.getLogger(__name__)

def safe_create_task(coro):
    """
    Create an asyncio task that logs exceptions instead of swallowing them.
    Fixes: 'Fire-and-Forget Task Exceptions' (Z.ai Review)
    """
    task = asyncio.create_task(coro)
    
    def log_exception(t):
        try:
            t.result()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[Background Task Error] Unhandled exception: {e}")
            traceback.print_exc()
            logger.exception("Background task failed with %s", e)

    task.add_done_callback(log_exception)
    return task
