from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from balthify2.schedule.config import config


class Sessions:
    @classmethod
    def make(cls):
        factory = cls._factory()
        return factory()

    @classmethod
    @lru_cache(maxsize=1)
    def _factory(cls):
        return sessionmaker(cls._engine(), class_=AsyncSession,
                            expire_on_commit=False)

    @classmethod
    @lru_cache(maxsize=1)
    def _engine(cls):
        return create_async_engine(config().db_url, encoding='utf-8')
