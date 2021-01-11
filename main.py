#!/usr/bin/env python
import os
from tornado.ioloop import IOLoop
from guardian import Guardian
from bot import NiceNotifyBot
from listener import make_app, DEFAULT_PORT

def main():
    auth_path = os.environ['BALTHIFY_AUTH_PATH']
    bot = NiceNotifyBot(os.environ['BALTHIFY_TOKEN'],
                        os.environ['BALTHIFY_CHAT_ID'])
    guard = Guardian()
    port = int(os.environ.get('BALTHIFY_LISTEN_PORT') or DEFAULT_PORT)
    app = make_app(auth_path, bot, guard)
    app.listen(port)
    IOLoop.current().start()

if __name__ == '__main__':
    main()
