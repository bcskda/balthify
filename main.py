#!/usr/bin/env python
from signal import signal, SIGINT, SIGTERM
from telegram.ext import Updater
from tornado.ioloop import IOLoop
from db_utils import SafeSessionFactory
from guard import Guard
from notify import NiceNotifier
from listener import make_app
from logs import get_logger
from scheduler import Scheduler
from config import Config

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
    updater = Updater(token=Config.tg_token)
    session_factory = SafeSessionFactory(Config.db_uri)
    scheduler = Scheduler(
        session_factory, updater,
        Config.chat_id, Config.admin_id
    )
    app = make_app(
        Config.auth_path,
        NiceNotifier(updater, Config.chat_id),
        Guard(session_factory)
    )

    prepare_signals()
    app.listen(Config.listen_port)
    updater.start_polling()
    IOLoop.current().start() # Will be stopped by signal handler
    logger.info('Stopped IOLoop')
    updater.stop()
    logger.info('Stopped Updater')
    session_factory.shutdown()
    logger.info('Stopped DB session factory')

if __name__ == '__main__':
    main()
