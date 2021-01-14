'''
Decides to accept/reject RTMP streams
'''
import functools
from db_models import ScheduledStream
from db_utils import SafeSessionFactory
from logs import get_logger

class Guard:
    def __init__(self, session_factory: SafeSessionFactory):
        self.logger = get_logger('guard {}'.format(id(self)))
        self.s_factory = session_factory

    # Publish event

    def check_publish(self, *args, **kwargs):
        try:
            self.log_publish_pre(*args, **kwargs)
            s_session = self.s_factory('future')
            query_cb = self.query_publish(*args, **kwargs)
            query_result = s_session.apply(query_cb).result()
            ok = self.validate_publish(query_result)
            self.log_publish_post(*args, **kwargs, granted=ok)
            return ok
        except Exception as e:
            logger.exception('publish: unhandled exception: %s', e)
            return False

    async def check_publish_async(self, *args, **kwargs):
        try:
            self.log_publish_pre(*args, **kwargs)
            s_session = self.s_factory('asyncio')
            query_cb = self.query_publish(*args, **kwargs)
            query_result = await s_session.apply(query_cb)
            ok = self.validate_publish(query_result)
            self.log_publish_post(*args, **kwargs, granted=ok)
            return ok
        except Exception as e:
            self.logger.exception('publish: unhandled exception: %s', e)
            return False

    def log_publish_pre(self, addr, app, name):
        self.logger.debug('publish: addr=%s app=%s name=%s', addr, app, name)

    @staticmethod
    def query_publish(addr, app, name):
        def cb(session):
            return session.query(ScheduledStream).filter_by(
                ingress_app=app, ingress_id=name
            ).all()
        return cb

    def validate_publish(self, query_result):
        self.logger.info('publish: match_list=%s', query_result)
        self.logger.warning('publish: unconditional accept')
        return True

    def log_publish_post(self, addr, app, name, granted):
        if granted:
            self.logger.info('publish granted: addr=%s app=%s name=%s',
                             addr, app, name)
        else:
            self.logger.info('publish denied: addr=%s app=%s name=%s',
                             addr, app, name)
