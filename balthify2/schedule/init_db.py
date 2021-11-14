import asyncio
import sys

from sqlalchemy.ext.asyncio import create_async_engine

from balthify2.common.models import metadata
from balthify2.schedule.config import config


async def async_main():
    url = config().db_url
    ack = input(f'Initialize database at {url}? y/n\n')
    if ack.lower() != 'y':
        sys.exit(1)

    engine = create_async_engine(url, encoding='utf-8')
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all, checkfirst=True)
    print('Done')


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_main())
    loop.close()


if __name__ == '__main__':
    main()
