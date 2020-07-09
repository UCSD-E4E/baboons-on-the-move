from typing import Dict, List, Tuple
from .Runner import Runner


class Serial(Runner):
    def __init__(self, name: str, *runners: List[Runner]):
        self._runners = runners

        Runner.__init__(self, name)

    def execute(self, state: Dict[str, any]) -> Tuple[bool, Dict[str, any]]:
        for runner in self._runners:
            success, state = runner.execute(state)

            if not success:
                return (False, state)

        return (True, state)
