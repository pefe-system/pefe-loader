CONFIG_FILE = "config.json"

from typing import List
from pefe_common.config import Config

schema = {
    "self": ({
        "host": (str, None),
        "port": (int, None),
        "benign_dir": (str, None),
        "malicious_dir": (str, None),
        "error_log_file": (str, "./error_log.txt"),
        "max_retries": (int, 5),
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
