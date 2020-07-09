from enum import Enum
from multiprocessing import Pool, cpu_count
from multiprocessing.pool import ThreadPool
from typing import Dict, List, Tuple
from .Runner import Runner


class ThreadType(Enum):
    PROCESS = 1
    THREAD = 2
    NONE = 3


class Parallel(Runner):
    def __init__(
        self,
        name: str,
        *runners: List[Runner],
        thread_type: ThreadType = ThreadType.PROCESS
    ):
        self._runners = runners

        if thread_type == ThreadType.PROCESS:
            self._pool = Pool(cpu_count())
        elif thread_type == ThreadType.THREAD:
            self._pool = ThreadPool(cpu_count())

        self._thread_type = thread_type

        Runner.__init__(self, name)

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        if (
            self.thread_type == ThreadType.PROCESS
            or self.thread_type == ThreadType.THREAD
        ):
            results = self._pool.map(
                [r.execute for r in self._runners], [state for r in self._runners]
            )
        elif self.thread_type == ThreadType.NONE:
            results = [r.execute(state) for r in self._runners]
        else:
            results = None  # This case doesn't exist, but satisfies Pyright.

        return_result = results[0]
        for result in results[1:]:
            return_result.update(result)

        success = any([s for s, _ in results])
        return (success, return_result)
