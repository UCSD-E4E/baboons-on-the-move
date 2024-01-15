from tqdm import tqdm

from bom_pipeline.progress import Progress

class TqdmProgress(Progress):
    def __init__(self) -> None:
        super().__init__()

        self._tqdm = tqdm()