'''
Notification bot with python-telegram-bot API
'''
from telegram.ext import Updater, CommandHandler

class NotifyBot:
    def __init__(self, token, chat_id):
        self._updater = Updater(token=token)
        self.chat_id = int(chat_id)

    def report(self, text):
        self._updater.bot.send_message(self.chat_id, text)

class NiceNotifyBot(NotifyBot):
    def report_connect(self, addr, app):
        mesg = '\n'.join([
            'Connect',
            f'addr={addr}',
            f'app={app}',
        ])
        self.report(mesg)

    def report_publish(self, addr, app, name):
        mesg = '\n'.join([
            'Publish',
            f'addr={addr}',
            f'app={app}',
            f'name={name}',
        ])
        self.report(mesg)

#def main():
#    logger = get_logger(__name__)
#    bot = NotifyBot(os.environ['BALTHIFY_TOKEN'],
#                    os.environ['BALTHIFY_CHAT_ID'])
#    bot.report(str(sys.argv))
#
#if __name__ == '__main__':
#    main()
