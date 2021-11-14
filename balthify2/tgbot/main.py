import logging
import signal

from telegram.ext import Updater, CommandHandler

from balthify2.tgbot.config import config
from balthify2.tgbot.handlers import ScheduleHandler


logger = logging.getLogger('balthify2.tgbot.main')


def stop_signals():
    return [
        signal.SIGINT,
        signal.SIGTERM,
    ]


def main():
    logging.basicConfig(level=logging.INFO)

    handler = ScheduleHandler()
    updater = Updater(token=config().token)
    updater.dispatcher.add_handler(
        CommandHandler('schedule', handler.on_schedule)
    )

    updater.start_polling()
    updater.idle()
