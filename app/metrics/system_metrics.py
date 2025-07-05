import os
import time
import asyncio
import psutil
import gc
from prometheus_client import Counter, Gauge

# Prefix all custom metrics with "fastapi_"
CPU_TIME = Counter(
    'fastapi_process_cpu_seconds_total',
    'Total CPU time consumed by this FastAPI process (user + system)'
)
RESIDENT_MEMORY = Gauge(
    'fastapi_process_resident_memory_bytes',
    'Resident memory (RSS) used by this FastAPI process'
)
VIRTUAL_MEMORY = Gauge(
    'fastapi_process_virtual_memory_bytes',
    'Virtual memory (VMS) allocated by this FastAPI process'
)
FILE_DESC_COUNT = Gauge(
    'fastapi_process_open_fds',
    'Number of open file descriptors for this FastAPI process'
)
THREAD_COUNT = Gauge(
    'fastapi_process_thread_count',
    'Number of threads in this FastAPI process'
)
PROCESS_START_TIME = Gauge(
    'fastapi_process_start_time_seconds',
    'Start time of this FastAPI process since unix epoch'
)
GC_COLLECTIONS = Gauge(
    'fastapi_python_gc_collections_total',
    'Number of garbage collections by generation in this FastAPI process',
    ['generation']
)

# Grab a handle on the current process
_process = psutil.Process(os.getpid())
_last_cpu = _process.cpu_times().user + _process.cpu_times().system

async def _collect_system_metrics(interval: int = 5):
    PROCESS_START_TIME.set(_process.create_time())

    global _last_cpu
    while True:
        # CPU delta
        current_cpu = _process.cpu_times().user + _process.cpu_times().system
        delta = current_cpu - _last_cpu
        CPU_TIME.inc(delta)
        _last_cpu = current_cpu

        # Memory
        mem = _process.memory_info()
        RESIDENT_MEMORY.set(mem.rss)
        VIRTUAL_MEMORY.set(mem.vms)

        # File descriptors
        try:
            FILE_DESC_COUNT.set(_process.num_fds())
        except AttributeError:
            FILE_DESC_COUNT.set(len(_process.open_files()))

        # Threads
        THREAD_COUNT.set(_process.num_threads())

        # GC stats
        counts = gc.get_count()
        for gen, count in enumerate(counts):
            GC_COLLECTIONS.labels(generation=str(gen)).set(count)

        await asyncio.sleep(interval)

def register_system_metrics(app, interval: int = None):
    if interval is None:
        interval = int(os.getenv('METRICS_INTERVAL', 5))

    @app.on_event('startup')
    async def start_system_metrics():
        asyncio.create_task(_collect_system_metrics(interval))
