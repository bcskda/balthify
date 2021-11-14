import json
import os
from functools import lru_cache

from pydantic import BaseModel


ENV_PREFIX = 'BALTHIFY2_'
ENV_JSON_PATH = ENV_PREFIX + 'JSON_PATH'


class Config(BaseModel):
    db_url: str


@lru_cache(maxsize=1)
def config():
    cfg = dict()

    # Read base from file
    if os.getenv(ENV_JSON_PATH):
        override = load_json(os.getenv(ENV_JSON_PATH))
        cfg.update(override)

    # Read overrides from env
    for key in Config.schema()['properties'].keys():
        env_key = ENV_PREFIX + key.upper()
        value = os.getenv(env_key)
        if value is not None:
            cfg.update({key: value})

    return Config(**cfg)


def load_json(path: str):
    with open(path) as conf:
        return json.load(conf)
