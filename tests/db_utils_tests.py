import asyncio
from db_models import ScheduledStream
from db_utils import SafeSessionFactory

def main():
    def query(session):
        return session.query(ScheduledStream).all()

    def test_future(factory):
        s_session = factory('future')
        assert s_session.apply(query).result() == []

    def test_asyncio(factory):
        async def routine(factory):
            s_session = factory('asyncio')
            assert await s_session.apply(query) == []

        asyncio.run(routine(factory))

    uri = 'sqlite:///db_utils_tests.sqlite3'
    factory = SafeSessionFactory(uri)
    test_future(factory)
    test_asyncio(factory)
    factory.shutdown()

if __name__ == '__main__':
    main()
