import json
import logging
import typing as tp
from datetime import datetime

from dateutil.parser import parse as dateutil_parse
from telegram.ext import CallbackContext
from tornado.httpclient import HTTPClient, HTTPRequest

from balthify2.common.models import RoutingRecord, RoutingRecordUserConfigurable
from balthify2.tgbot.config import config


class ScheduleHandler:
    logger = logging.getLogger('balthify2.tgbot.handlers.schedule')

    class Composer:
        def __init__(self, record: RoutingRecord):
            self.record = record

        def shareable_reply(self) -> str:
            play_url = (
                config().dataserver_base_url
                + self.record.egress_app
                + '/'
                + self.record.egress_id)

            return '\n'.join([
                'Stream scheduled, forward this message to viewers',
                '',
                f'Title: {self.record.title}',
                f'Start/end: {self.record.start_time} ~ {self.record.end_time}',
                'Description:',
                self.record.description,
                '',
                'Public play URL:',
                play_url
            ])

        def secret_reply(self) -> str:
            publish_url = (
                config().dataserver_base_url
                + self.record.ingress_app
                + '/'
                + self.record.ingress_id)

            return '\n'.join([
                'This message is only for publisher',
                '',
                'Publish URL:',
                publish_url
            ])


    def record(self, command_args: tp.List[str]) -> RoutingRecordUserConfigurable:
        title, start_time, end_time = command_args[:3]
        description = ' '.join(command_args[3:])

        start_time=dateutil_parse(start_time)
        end_time=dateutil_parse(end_time)
        if start_time.tzinfo is None or end_time.tzinfo is None:
            raise ValueError('Timezone must be explicitly specified')
        elif start_time.tzinfo != end_time.tzinfo:
            raise ValueError('Start and end timezones must match')

        return RoutingRecordUserConfigurable(
            start_time=start_time,
            end_time=end_time,
            title=title,
            description=description,
            ingress_app=config().ingress_app,
            egress_app=config().egress_app
        )

    def try_schedule(self, record: RoutingRecordUserConfigurable) -> RoutingRecord:
        client = HTTPClient()
        response = client.fetch(
            config().schedule_api_url,
            method='POST',
            body=record.json(),
            headers={
                'Content-Type': 'application/json'
            }
        )
        return RoutingRecord(**json.loads(response.body))

    def on_schedule(self, update, ctx: CallbackContext) -> None:
        chat_id = update.effective_chat.id
        if str(chat_id) not in config().admin_ids:
            self.logger.warning('Ignoring unauthorized command: chat=%s args=%s',
                        update.effective_chat.id, ctx.args)
            return
        if not update.message:
            self.logger.info('Likely edited message, ignoring: chat=%s', chat_id)
            return
        self.logger.info('Authorized: chat=%s args=%s', chat_id, ctx.args)

        try:
            record = self.record(ctx.args)
            self.logger.info('Parsed: chat=%s record=%s', chat_id, record)
            record = self.try_schedule(record)
            self.logger.info('Scheduled: chat=%s record=%s', chat_id, record)
            composer = self.Composer(record)

            shareable_text = composer.shareable_reply()
            shareable_msg = update.message.reply_text(
                shareable_text,
                reply_to_message_id=update.effective_message.message_id)

            secret_text = composer.secret_reply()
            shareable_msg.reply_text(
                secret_text,
                reply_to_message_id=shareable_msg.message_id)
        except Exception as e:
            self.logger.exception(
                'Exception while processing chat_id=%s, args=%s',
                chat_id,
                ctx.args)
            update.message.reply_text(f'Exception: {e}')
