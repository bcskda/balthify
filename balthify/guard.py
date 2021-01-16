'''
Decides to accept/reject RTMP streams
'''
from datetime import datetime
import functools
from balthify.db_models import RoutingRecord
from balthify.db_utils import SafeSessionFactory
from balthify.logs import get_logger

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
            redir = self.validate_publish(query_result)
            self.log_publish_post(*args, **kwargs, redir=redir)
            return redir
        except Exception as e:
            logger.exception('publish: unhandled exception: %s', e)
            return False

    async def check_publish_async(self, *args, **kwargs):
        try:
            self.log_publish_pre(*args, **kwargs)
            s_session = self.s_factory('asyncio')
            query_cb = self.query_publish(*args, **kwargs)
            query_result = await s_session.apply(query_cb)
            redir = self.validate_publish(query_result)
            self.log_publish_post(*args, **kwargs, redir=redir)
            return redir
        except Exception as e:
            self.logger.exception('publish: unhandled exception: %s', e)
            return False

    def log_publish_pre(self, addr, app, name):
        self.logger.debug('publish: addr=%s app=%s name=%s', addr, app, name)

    @staticmethod
    def query_publish(addr, app, name):
        def cb(session):
            now = datetime.now()
            return session.query(RoutingRecord).filter(
                RoutingRecord.start_time <= now,
                now < RoutingRecord.end_time,
                RoutingRecord.ingress_app == app,
                RoutingRecord.ingress_id == name,
            ).all()
        return cb

    def validate_publish(self, query_result) -> '(app, id, title) or None':
        '''Redirect, or None if invalid'''
        self.logger.debug('publish: match_list=%s', query_result)
        if len(query_result) < 1:
            self.logger.info('publish: unregistered stream')
            return None
        if len(query_result) > 1:
            ids = map(lambda r: r['routing_id'], query_result.fetchall())
            self.logger.warning('publish: streams overlap: %s', list(ids))
            return None
        row = query_result[0]
        redir_app, redir_id = row.egress_app, row.egress_id
        self.logger.info('publish: redirect to (%s, %s)', redir_app , redir_id)
        return redir_app, redir_id, row.title

    def log_publish_post(self, addr, app, name, redir):
        if redir:
            self.logger.info('publish granted: addr=%s app=%s name=%s',
                             addr, app, name)
        else:
            self.logger.info('publish denied: addr=%s app=%s name=%s',
                             addr, app, name)
