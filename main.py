#!/usr/bin/env python
import os
from signal import signal, SIGINT, SIGTERM
from telegram.ext import Updater
from tornado.ioloop import IOLoop
from db_utils import SafeSessionFactory
from guard import Guard
from notify import NiceNotifier
from listener import make_app, DEFAULT_PORT
from logs import get_logger
from scheduler import Scheduler

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
    chat_id = os.environ['BALTHIFY_CHAT_ID']
    admin_id = os.environ['BALTHIFY_ADMIN_ID']
    updater = Updater(token=os.environ['BALTHIFY_TOKEN'])
    notifier = NiceNotifier(updater, chat_id)
    session_factory = SafeSessionFactory(os.environ['BALTHIFY_DB_URI'])
    scheduler = Scheduler(
        session_factory, updater,
        chat_id, admin_id
    )
    guard = Guard(session_factory)
    port = int(os.environ.get('BALTHIFY_LISTEN_PORT') or DEFAULT_PORT)
    app = make_app(auth_path, notifier, guard)

    prepare_signals()
    app.listen(port)
    updater.start_polling()
    IOLoop.current().start() # Will be stopped by signal handler
    logger.info('Stopped IOLoop')
    updater.stop()
    logger.info('Stopped Updater')
    session_factory.shutdown()
    logger.info('Stopped DB session factory')

if __name__ == '__main__':
    main()
