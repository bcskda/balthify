#!/usr/bin/env python
import os
from signal import signal, SIGINT, SIGTERM
from telegram.ext import Updater
from tornado.ioloop import IOLoop
from guard import Guard
from notify import NiceNotifier
from listener import make_app, DEFAULT_PORT
from logs import get_logger

STOP_SIGNALS = [SIGINT, SIGTERM]

logger = get_logger('main')

def prepare_signals():
    def stop_ioloop(signo):
        IOLoop.current().stop()

    def stop_on_signal(signo, frame):
        logger.info('Stopping IOLoop on signal %s', signo)
        # Sync-edly request IOLoop stop
        IOLoop.current().add_callback_from_signal(stop_ioloop, signo)

    for signo in STOP_SIGNALS:
        signal(signo, stop_on_signal)

def main():
    auth_path = os.environ['BALTHIFY_AUTH_PATH']
    updater = Updater(token=os.environ['BALTHIFY_TOKEN'])
    notifier = NiceNotifier(updater, os.environ['BALTHIFY_CHAT_ID'])
    guard = Guard()
    port = int(os.environ.get('BALTHIFY_LISTEN_PORT') or DEFAULT_PORT)
    app = make_app(auth_path, notifier, guard)

    prepare_signals()
    app.listen(port)
    updater.start_polling()
    IOLoop.current().start() # Will be stopped by signal handler
    logger.info('Stopped IOLoop')
    updater.stop()
    logger.info('Stopped Updater')

if __name__ == '__main__':
    main()
