import json
import os
import typing as tp
from functools import lru_cache

from pydantic import BaseModel, AnyUrl, HttpUrl, validator


ENV_PREFIX = 'BALTHIFY2_TGBOT_'
ENV_JSON_PATH = ENV_PREFIX + 'JSON_PATH'


class Config(BaseModel):
    token: str
    admin_ids: tp.List[str]
    ingress_app: str
    egress_app: str
    schedule_api_url: AnyUrl
    dataserver_base_url: AnyUrl

    @validator('dataserver_base_url')
    def dataserver_base_url_endswith_slash(cls, v):
        assert v.endswith('/')
        return v

    @validator('admin_ids', pre=True)
    def maybe_comma_separated(cls, v):
        if isinstance(v, str):
            return v.split(',')
        else:
            return v


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
