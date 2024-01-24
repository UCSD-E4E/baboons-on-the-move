from typing import Dict

from bom_pipeline.config import Config

from library.config import get_config_part


class LibraryConfig(Config):
    def __init__(self) -> None:
        super().__init__()

    def get_part(self, key: str) -> Dict:
        return get_config_part(key)
