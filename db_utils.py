from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_models import metadata
from sync_utils import BaseSafeSession, AwaitableSafeSession, FutureSafeSession
from logs import get_logger

logger = get_logger('db_utils')

engine = None
session_factory = None

def init_engine(uri):
    '''Throws ValueError if called twice.'''
    if engine is not None:
        raise ValueError('engine already initialized')
    logger.info('initializing engine')
    engine = create_engine(uri, encoding='utf-8')
    metadata.create_all(engine, checkfirst=True)
    session_factory = sessionmaker(engine)
    logger.info('initialized engine')

session = None
session_executor = ThreadPoolExecutor(max_workers=1)

SAFE_CLASSES = {
    'future': FutureSafeSession,
    'awaitable': AwaitableSafeSession
}

def _init_session():
    if session is not None:
        raise ValueError('session already initialized')

    def _do_init_session():
        session = session_factory()
        logger.info('initialized session')

    logger.info('initializing session')
    session_executor.submit(_do_init_session).result()

def get_session(kind: str):
    '''Get a safe-wrapper for session.

    Arguments:
    kind: 'future' or 'awaitable'
    '''
    if session is None:
        _init_session()
    return safety_classes[kind](session, session_executor)

def shutdown():
    '''Properly shutdown serial executor and close session'''
    def _do_close_sessions():
        session_factory.close_all()
        logger.info('closed all sessions')

    logger.info('closing all sessions')
    logger.info('stopping session executor')
    session_executor.submit(_do_close_sessions)
    session_executor.shutdown()
    logger.info('stopped session executor')
