import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime


class InMemoryTaskQueue:
    def __init__(self, max_workers=2):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._tasks = {}
        self._lock = threading.Lock()

    def enqueue(self, fn, *args, metadata=None, **kwargs):
        task_id = str(uuid.uuid4())
        with self._lock:
            self._tasks[task_id] = {
                "status": "queued",
                "result": None,
                "error": None,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
            }
        self.executor.submit(self._run_task, task_id, fn, *args, **kwargs)
        return task_id

    def _run_task(self, task_id, fn, *args, **kwargs):
        with self._lock:
            self._tasks[task_id]["status"] = "running"
        try:
            result = fn(*args, **kwargs)
            with self._lock:
                self._tasks[task_id]["status"] = "completed"
                self._tasks[task_id]["result"] = result
        except Exception as exc:  # pragma: no cover - defensive branch
            with self._lock:
                self._tasks[task_id]["status"] = "failed"
                self._tasks[task_id]["error"] = str(exc)

    def get(self, task_id):
        with self._lock:
            task = self._tasks.get(task_id)
            return dict(task) if task else None
