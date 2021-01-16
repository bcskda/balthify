'''
Bot's scheduler feature
'''
from datetime import datetime
import itertools
import secrets
import string
from telegram.ext import Updater, CallbackContext, CommandHandler
from db_models import RoutingRecord
from notify import NiceNotifier
from logs import get_logger
from config import Config

logger = get_logger('scheduler')

class Scheduler:
    def __init__(self, session_factory, updater, chat_id, admin_id):
        self.s_session = session_factory('future')
        self.updater = updater
        self.notifier = NiceNotifier(updater, chat_id)
        self.admin_id = int(admin_id)
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler('schedule', self.on_schedule))

    def on_schedule(self, update, ctx: CallbackContext):
        if update.effective_chat.id != self.admin_id:
            logger.info('ignoring unauthorized command: chat_id=%s args=%s',
                        update.effective_chat.id, ctx.args)
            return
        title, start, end = ctx.args[:3]
        description = ' '.join(ctx.args[3:])
        record = dict(
            ingress_app=Config.ingress_app,
            ingress_id=self._random_id(12),
            egress_app=Config.egress_app,
            egress_id=self._random_id(12),
            start_time=datetime.fromisoformat(start),
            end_time=datetime.fromisoformat(end),
            description=description,
            title=title
        )
        self.s_session.apply(self._make_insert_record(record)) \
            .result()
        publish_url = Config.access_template.format(
            record['ingress_app'], record['ingress_id']
        )
        watch_url = Config.access_template.format(
            record['egress_app'], record['egress_id']
        )
        update.message.reply_text('\n'.join([
            'Stream scheduled',
            'Uplink url:',
            publish_url,
            'Watch url:',
            watch_url
        ]))
        self.notifier.report_schedule(
            record['title'], record['description'],
            watch_url, record['start_time']
        )

    @staticmethod
    def _make_insert_record(record_kwargs):
        def act(session):
            session.add(RoutingRecord(**record_kwargs))
            session.commit()
        return act

    @staticmethod
    def _random_id(length: int) -> str:
        _ID_CHARSET = string.ascii_lowercase + string.digits
        return ''.join(map(
            secrets.choice,
            itertools.repeat(_ID_CHARSET, length)
        ))
