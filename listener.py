'''
Tornado handlers and application for nginx-module-rtmp callbacks

exports: make_app

See https://github.com/arut/nginx-rtmp-module/wiki/Directives#notify
'''
from functools import partial
from tornado.web import Application, RequestHandler, MissingArgumentError
from logs import get_logger
from notify import NiceNotifier
from guard import Guard
from config import Config

class ModRtmpConst:
    ST_ACCEPT = 200
    ST_INVALID = 400
    ST_REJECT = 403

    _mod_rtmp_arguments = {
        'connect': [ 'addr', 'app' ],
        'publish': [ 'addr', 'app', 'name' ],
        'play': [ 'addr', 'app', 'name' ],
    }

class BaseHandler(ModRtmpConst, RequestHandler):
    def initialize(self, call_method, logger):
        self.call_method = call_method
        self.logger = logger

    async def post_validated(self, *args):
        '''Implement in subclass; args as in _mod_rtmp_arguments'''
        raise NotImplementedError

    async def post(self):
        args = self._validate_args()
        if args:
            await self.post_validated(**args)
        else:
            self.send_error(self.ST_INVALID)

    def _validate_args(self) -> dict or None:
        '''Dict of args as in _mod_rtmp_arguments if valid, else None'''
        try:
            assert self.request.headers.get('Content-Type') \
                == 'application/x-www-form-urlencoded'
            assert self.get_argument('call', default=None) == self.call_method
            return self._get_method_args(no_raise=False)
        except AssertionError or MissingArgumentError:
            self.logger.warning('invalid request: %s',
                                self._get_method_args(no_raise=True))
            return False

    def _get_method_args(self, no_raise=True):
        if no_raise:
            getter = partial(self.get_argument, default=None)
        else:
            getter = self.get_argument
        return dict(map(
            lambda k: (k, getter(k)),
            self._mod_rtmp_arguments[self.call_method]
        ))

class ConnectHandler(BaseHandler):
    def initialize(self, notifier, guard):
        super(ConnectHandler, self).initialize(
            'connect',
            get_logger('listen.on_connect')
        )
        self.notifier = notifier
        self.guard = guard

    async def post_validated(self, addr, app):
        self.logger.debug('addr=%s, app=%s', addr, app)
        #if self.guard.check_connect(addr, app):
        self.set_status(self.ST_ACCEPT)
        #else:
        #    self.send_error(self.ST_REJECT)

class PublishHandler(BaseHandler):
    def initialize(self, notifier, guard):
        super(PublishHandler, self).initialize(
            'publish',
            get_logger('listen.on_publish')
        )
        self.notifier = notifier
        self.guard = guard

    async def post_validated(self, addr, app, name):
        self.logger.debug('addr=%s, app=%s, name=%s', addr, app, name)
        redir = await self.guard.check_publish_async(addr, app, name)
        if redir:
            redir_app, redir_id = redir
            self.logger.info('redirect to %s, %s', redir_app, redir_id)
            self.redirect(Config.redirect_template.format(redir_app, redir_id))
            self.notifier.report_publish(redir_app, redir_id)
        else:
            self.send_error(self.ST_REJECT)

def make_app(auth_path, notifier: NiceNotifier, guard: Guard):
    def make_handler(pair):
        method, handler = pair
        return (
            auth_path + f'/on_{method}',
            handler,
            dict(notifier=notifier, guard=guard)
        )
    
    routes = [
        ('connect', ConnectHandler),
        ('publish', PublishHandler),
    ]
    return Application(list(map(make_handler, routes)))
