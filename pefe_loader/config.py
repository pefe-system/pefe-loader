CONFIG_FILE = "config.json"

from typing import List
from .pefe_common.config import Config

nested_item_schema = {
    "name": (str, None),
    "value": (int, None)
}

schema = {
    "self": ({
        "host": (str, None),
        "port": (int, 8080)
    }, None),

    "debug": (bool, False),

    # More examples:
    # "allowed_ips": (List[str], []),  # list of strings
    # "thresholds": (List[int], None, "Thresholds must be provided and be integers."),
    # "nested_list": (List[nested_item_schema], [])
}

config = Config.load(schema, CONFIG_FILE)

# Examples
# print(config["self"]["host"])         # nested get
# print(config["allowed_ips"])            # list[str]
# print(config["nested_list"][0]["name"]) # list of nested dicts
