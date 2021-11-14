import logging
import signal

from telegram.ext import Updater

from balthify2.tgbot.config import config
from balthify2.tgbot.handlers import Handler, Notifier


logger = logging.getLogger('balthify2.tgbot.main')


def stop_signals():
    return [
        signal.SIGINT,
        signal.SIGTERM,
    ]


def main():
    logging.basicConfig(level=logging.INFO)

    notifier = Notifier()
    handler = Handler(notifier)
    updater = Updater(token=config().token)
    for callback in handler.callback_handlers():
        updater.dispatcher.add_handler(callback)

    updater.start_polling()
    updater.idle()
