import asyncio
import time

"""
Leding: Here the main point is to show that line #10 or #11's different bahavior.
#10: fn() is blocked.
#11: non-blocking. Control returns to the event loop but since there is no concurrent tasks
    yet, the event loop will wait for the sleep to finish before moving on to the next line.
    This result the same behavior to #10. Should there be other tasks scheduled, the event loop,
    they wil be executed concurrently.
"""
async def fn(blocking_sleep=False):
    print("one")
    if blocking_sleep:
        time.sleep(1)  # Blocking sleep
    else:
        await asyncio.sleep(1)  # Non-blocking sleep
    
    task = asyncio.create_task(fn2())  # Schedule fn2
    print("four")
    await asyncio.sleep(1)  # Non-blocking sleep
    await task
    print("five")

async def fn2():
    await asyncio.sleep(1)  # Non-blocking sleep
    print("two")
    await asyncio.sleep(1)  # Non-blocking sleep
    print("three")

# Test with blocking sleep
print("With Blocking Sleep:")
asyncio.run(fn(blocking_sleep=True))

# Test with non-blocking sleep
print("\nWith Non-Blocking Sleep:")
asyncio.run(fn(blocking_sleep=False))
