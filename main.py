#!/usr/bin/env python
import os
from signal import signal, SIGINT, SIGTERM
from tornado.ioloop import IOLoop
from guard import Guard
from bot import NiceNotifyBot
from listener import make_app, DEFAULT_PORT

STOP_SIGNALS = [SIGINT, SIGTERM]

def prepare_signals():
    def stop_ioloop(signo):
        IOLoop.current().stop()
        print(f'Stopped IOLoop on signal {signo}')

    def stop_on_signal(signo, frame):
        print(f'Stopping IOLoop on signal {signo}')
        # Sync-edly request IOLoop stop
        IOLoop.current().add_callback_from_signal(stop_ioloop, signo)

    for signo in STOP_SIGNALS:
        signal(signo, stop_on_signal)

def main():
    auth_path = os.environ['BALTHIFY_AUTH_PATH']
    bot = NiceNotifyBot(os.environ['BALTHIFY_TOKEN'],
                        os.environ['BALTHIFY_CHAT_ID'])
    guard = Guard()
    port = int(os.environ.get('BALTHIFY_LISTEN_PORT') or DEFAULT_PORT)
    app = make_app(auth_path, bot, guard)

    prepare_signals()
    app.listen(port)
    bot.updater.start_polling()
    IOLoop.current().start() # Will be stopped by signal handler
    bot.updater.stop()

if __name__ == '__main__':
    main()
