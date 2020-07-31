"""
Implements a parallel pipeline.
"""

from enum import Enum
from multiprocessing import Pool, cpu_count
from multiprocessing.pool import ThreadPool
from typing import Dict, List, Tuple

from .stage import Stage


class ThreadType(Enum):
    """
    Represents how threads should be impelmented
    """

    PROCESS = 1
    THREAD = 2
    NONE = 3


class Parallel(Stage):
    """
    A parallel pipeline which can be used to logically organize stages.
    """

    def __init__(
        self,
        name: str,
        *stages: List[Stage],
        thread_type: ThreadType = ThreadType.PROCESS
    ):
        Stage.__init__(self)

        self.name = name
        self._stages = stages

        if thread_type == ThreadType.PROCESS:
            self._pool = Pool(cpu_count())
        elif thread_type == ThreadType.THREAD:
            self._pool = ThreadPool(cpu_count())

        self._thread_type = thread_type

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        """
        Runs multiple stages in parallel.
        """

        if (
            self._thread_type == ThreadType.PROCESS
            or self._thread_type == ThreadType.THREAD
        ):
            results = self._pool.map(
                [s.execute for s in self._stages], [state for s in self._stages]
            )
        elif self._thread_type == ThreadType.NONE:
            results = [s.execute(state) for s in self._stages]
        else:
            results = None  # This case doesn't exist, but satisfies Pyright.

        return_result = results[0]
        for result in results[1:]:
            return_result.update(result)

        success = any([s for s, _ in results])
        return (success, return_result)
