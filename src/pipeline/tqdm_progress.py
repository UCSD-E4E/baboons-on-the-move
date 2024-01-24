from bom_pipeline.progress import Progress
from tqdm import tqdm


class TqdmProgress(Progress):
    def __init__(self) -> None:
        super().__init__()

        self._tqdm: tqdm = tqdm()

    @property
    def progress(self) -> int:
        return self._tqdm.pos

    @progress.setter
    def progress(self, value: int):
        self._tqdm.update(value - self._tqdm.pos)

    @property
    def total(self) -> int:
        return self._tqdm.total

    @total.setter
    def total(self, value: int):
        self._tqdm.total = value

    def close(self):
        if self._tqdm is not None:
            self._tqdm.close()

    def write(self, s: str):
        self._tqdm.write(s)
