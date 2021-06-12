from typing import Dict, Callable, List
from pipeline.serial import Serial
from config import get_config_part


class ConfigSerial(Serial):
    def __init__(
        self,
        name: str,
        config_key: str,
        runtime_config: Dict[str, any],
        *stage_types: List[Callable]
    ):
        config_part = get_config_part(config_key)
        types = [(s, config_part[s.__name__]) for s in stage_types]
        types.sort(key=lambda x: x[1]["order"])

        selected_types = [t for t, c in types if c["enabled"] == 1]

        Serial.__init__(self, name, runtime_config, *selected_types)
