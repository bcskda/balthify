from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from balthify.db_models import metadata
from balthify.logs import get_logger
from balthify.sync_utils import BaseSafeWrapper, AwaitableSafeWrapper, FutureSafeWrapper

logger = get_logger('db_utils')

class SafeSessionFactory:
    SAFE_CLASSES = {
        'future': FutureSafeWrapper,
        'asyncio': AwaitableSafeWrapper
    }

    def __init__(self, uri):
        self.engine = create_engine(uri, encoding='utf-8')
        metadata.create_all(self.engine, checkfirst=True)
        self.factory = sessionmaker(bind=self.engine)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.session = self.executor.submit(self.factory).result()

    def __call__(self, kind: str):
        return self.SAFE_CLASSES[kind](self.session, self.executor)

    def shutdown(self):
        logger.debug('shutting down sessions')
        self.executor.submit(self.session.close).result()
        logger.debug('shut down sessions')
        logger.debug('shutting down executor')
        self.executor.shutdown()
        logger.debug('shut down executor')
        logger.info('shut down id={}'.format(id(self)))
