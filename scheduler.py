'''
Bot's scheduler feature
'''
from datetime import datetime
from telegram.ext import Updater, CallbackContext, CommandHandler
from db_models import ScheduledStream
from notify import NiceNotifier

class Scheduler:
    def __init__(self, session_factory, updater, chat_id, admin_id):
        self.s_session = session_factory('future')
        self.updater = updater
        self.notifier = NiceNotifier(updater, chat_id)
        self.admin_id = int(admin_id)
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler('schedule', self.on_schedule))

    def on_schedule(self, update, ctx: CallbackContext):
        title, start, ingress_id = ctx.args[:3]
        start = datetime.fromisoformat(start)
        egress_app = 'test_app_egress'
        egress_id = 'random_egress_id'
        new_item = ScheduledStream(
            ingress_app='secret_app',
            ingress_id=ingress_id,
            egress_app=egress_app,
            egress_id=egress_id,
            start_time=start
        )
        self.s_session.apply(
            lambda session: session.add(new_item)
        ).result()
        self.notifier.report_schedule(
            title, 'rtmp://balthasar', egress_app, egress_id, start
        )
