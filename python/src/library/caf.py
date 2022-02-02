"""
Module for requesting disabling sleep.
Depends on https://github.com/clcrutch/caffeinate
"""
from shutil import which
from subprocess import Popen, PIPE


class Caffine:
    """
    Manages requests for disabling sleep.
    """
    def __init__(self):
        self._current_id = 0
        self._requests = []
        self._process: Popen = None

    def _start_process(self):
        file_path = which("caf")

        if not file_path:
            return

        self._process = Popen([file_path], stdin=PIPE)
        self._process.__enter__()

    def _kill_process(self):
        self._process.communicate(" ")
        self._process.kill()
        self._process.__exit__()

    def request(self) -> int:
        """
        Submits a request to prevent sleep.  Returns an identifier for the request.
        """

        current_id = self._current_id
        self._current_id += 1

        if not self._requests:
            self._start_process()

        self._requests.append(self._current_id)

        return current_id

    def release(self, identity: int):
        """
        Takes the ID from a previous requests and removes it from the list of requests.
        If it is the last request, then stop requesting to prevent sleep.
        """
        if identity not in self._requests:
            return

        self._requests.remove(identity)

        if not self._requests:
            self._kill_process()
