"""
C13 · ADVANCED · CONCURRENCY: threads, processes, asyncio
═══════════════════════════════════════════════════════════════════════════════════════════════
BIG HOOK  "Threads for WAITING, processes for THINKING, asyncio for LOTS of waiting."
          The GIL lets only ONE thread run Python code at a time, but a thread that is WAITING
          (network, disk, sleep) releases it, so I/O work still overlaps nicely.

  Work type                         Tool                                    QA example
  I/O-bound (HTTP, DB, files)       ThreadPoolExecutor  /  asyncio          call 50 APIs in parallel
  CPU-bound (parsing, hashing)      ProcessPoolExecutor / multiprocessing   analyse huge logs
  Many test FILES in parallel       pytest-xdist (processes)                pytest -n auto

Run:  python -m pytest python/Python_Examples/Concepts/test_c13_concurrency.py -v
"""

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def fake_api_call(endpoint: str, delay: float = 0.1) -> str:
    time.sleep(delay)  # stands in for network wait (releases the GIL)
    return f"{endpoint}: 200"


ENDPOINTS = ["/products", "/brands", "/users", "/orders", "/carts"]


# ── 1. ThreadPoolExecutor: PARALLEL I/O ─────────────────────────────────────────────────────
# HOOK  "A pool = a team of workers; map hands out the jobs and KEEPS THE ORDER."
def test_thread_pool_runs_io_in_parallel():
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=5) as pool:  # `with` waits for all and shuts down
        results = list(pool.map(fake_api_call, ENDPOINTS))
    elapsed = time.perf_counter() - start
    assert results[0] == "/products: 200"  # same order as the input
    assert elapsed < 0.4  # ~0.1 s total instead of 0.5 s one by one


def test_as_completed_and_errors():
    # HOOK  "submit = one job, Future = its receipt, as_completed = receipts as they finish"
    def maybe_fail(endpoint: str) -> str:
        if endpoint == "/orders":
            raise ConnectionError("503")
        return fake_api_call(endpoint, 0.01)

    ok, failed = [], []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(maybe_fail, e): e for e in ENDPOINTS}
        for future in as_completed(futures):  # FINISH order, not submit order
            try:
                ok.append(future.result())  # .result() RE-RAISES the worker's exception here
            except ConnectionError:
                failed.append(futures[future])
    assert failed == ["/orders"] and len(ok) == 4


# ── 2. RACE CONDITIONS AND LOCKS ────────────────────────────────────────────────────────────
# HOOK  "Shared + mutable + threads = a race. A Lock = one person in the room at a time."
class Counter:
    def __init__(self) -> None:
        self.value = 0
        self._lock = threading.Lock()

    def unsafe_increment(self) -> None:
        current = self.value  # read…
        time.sleep(0)  # …let another thread jump in (exaggerates the race)…
        self.value = current + 1  # …write back a STALE value

    def safe_increment(self) -> None:
        with self._lock:  # only one thread inside at a time
            current = self.value
            time.sleep(0)
            self.value = current + 1


def run_threads(target, n_threads: int = 8, per_thread: int = 200) -> None:
    def work():
        for _ in range(per_thread):
            target()

    threads = [threading.Thread(target=work) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()  # wait for each to finish


def test_lock_prevents_lost_updates():
    safe = Counter()
    run_threads(safe.safe_increment)
    assert safe.value == 8 * 200  # always exact
    # unsafe_increment usually ends BELOW 1600 (lost updates). Not asserted: races are
    # non-deterministic, which is exactly why they cause flaky tests.


# ── 3. asyncio: ONE THREAD, MANY WAITS ──────────────────────────────────────────────────────
# HOOK  "async def = can PAUSE; await = 'pause here, do other work until this is ready';
#        gather = start them all, wait for all."
async def fetch(endpoint: str, delay: float = 0.1) -> str:
    await asyncio.sleep(delay)  # NEVER time.sleep inside async code: it blocks everything
    return f"{endpoint}: 200"


async def fetch_all() -> list[str]:
    return await asyncio.gather(*(fetch(e) for e in ENDPOINTS))  # concurrent, order kept


def test_asyncio_gather():
    start = time.perf_counter()
    results = asyncio.run(fetch_all())  # asyncio.run = start the event loop (from sync code)
    assert len(results) == 5 and results[-1] == "/carts: 200"
    assert time.perf_counter() - start < 0.4


def test_asyncio_timeout():
    async def slow():
        async with asyncio.timeout(0.05):  # 3.11+: cancel if it takes too long
            await asyncio.sleep(1)

    try:
        asyncio.run(slow())
        raised = False
    except TimeoutError:
        raised = True
    assert raised


def test_async_task_group_collects_errors():
    # HOOK  "TaskGroup = a team that stops together": one failure cancels the rest and all
    #        errors come back as an ExceptionGroup (see C07 except*).
    async def boom():
        raise ValueError("bad response")

    async def main():
        async with asyncio.TaskGroup() as tg:
            tg.create_task(fetch("/ok", 0.5))
            tg.create_task(boom())

    try:
        asyncio.run(main())
        errors = []
    except* ValueError as group:
        errors = [str(e) for e in group.exceptions]
    assert errors == ["bad response"]


"""
 PLAYWRIGHT NOTE
   playwright.sync_api  → normal functions, what pytest-playwright uses by default
   playwright.async_api → async/await version; needs pytest-asyncio or asyncio.run
   Don't mix the two in one test. For parallel BROWSER tests use pytest-xdist (processes).

SELF-CHECK
  1. 50 HTTP calls to speed up: threads or processes?     → threads (or asyncio): I/O-bound
  2. What does the GIL prevent?                           → two threads running Python bytecode at once
  3. future.result() when the worker raised?              → re-raises that exception
  4. time.sleep inside async def: what happens?           → blocks the whole event loop
  5. How do you stop lost updates on a shared counter?    → a threading.Lock (or don't share)
"""
