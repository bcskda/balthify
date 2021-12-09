from pydantic import BaseSettings


class Config(BaseSettings):
    lookup_url: str
    redirect_domain: str

    class Config:
        env_prefix = 'BALTHIFY2_ACL_'
        case_sensitive = False
