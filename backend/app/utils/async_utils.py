import asyncio
import threading
from typing import Coroutine, TypeVar

T = TypeVar("T")

def run_async_synchronous(coro: Coroutine[None, None, T]) -> T:
    """
    Runs an async coroutine from a synchronous context.
    If an event loop is already running in the current thread (nesting),
    it runs the coroutine in a separate thread to avoid RuntimeError.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No loop in current thread, safe to use asyncio.run
        return asyncio.run(coro)

    # Loop is running, we cannot use asyncio.run or loop.run_until_complete
    # We use a thread to run the coroutine and wait for the result.
    result = []
    exception = []

    def target():
        try:
            result.append(asyncio.run(coro))
        except Exception as e:
            exception.append(e)

    thread = threading.Thread(target=target)
    thread.start()
    thread.join()

    if exception:
        raise exception[0]
    return result[0]
