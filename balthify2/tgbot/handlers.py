from datetime import datetime
import logging
import typing as tp

from dateutil.parser import parse as dateutil_parse
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Dispatcher,
    Updater,
)

from balthify2.common.models import RoutingRecordUserConfigurable
from balthify2.tgbot.config import config


logger = logging.getLogger('balthify2.tgbot.handlers')


class Notifier:
    pass


class Handler:
    def __init__(self, notifier: Notifier):
        self.notifier = notifier

    def callback_handlers(self) -> tp.List[CommandHandler]:
        return [
            CommandHandler('schedule', self.on_schedule),
        ]

    def record(self, command_args: tp.List[str]) -> RoutingRecordUserConfigurable:
        title, start_time, end_time = command_args[:3]
        description = ' '.join(command_args[3:])

        return RoutingRecordUserConfigurable(
            start_time=dateutil_parse(start_time),
            end_time=dateutil_parse(end_time),
            title=title,
            description=description,
            ingress_app=config().ingress_app,
            egress_app=config().egress_app
        )

    def on_schedule(self, update, ctx: CallbackContext) -> None:
        chat_id = update.effective_chat.id
        if str(chat_id) not in config().admin_ids:
            logger.warning('Ignoring unauthorized command: chat=%s args=%s',
                        update.effective_chat.id, ctx.args)
            return
        if not update.message:
            logger.info('Likely edited message, ignoring: chat=%s', chat_id)
            return
        logger.info('Authorized: chat=%s args=%s', chat_id, ctx.args)

        record = self.record(ctx.args)
        logger.info('Parsed: chat=%s record=%s', chat_id, record)
