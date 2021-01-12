'''
Notification bot with python-telegram-bot API
'''
from telegram.ext import Updater, CommandHandler

class NotifyBot:
    def __init__(self, token, chat_id):
        self.updater = Updater(token=token)
        self.chat_id = int(chat_id)

    def report_unsafe(self, text):
        '''Call bot.send_message from this thread'''
        self.updater.bot.send_message(self.chat_id, text)

    def report(self, text):
        '''Schedule sync-ed bot.send_message'''
        job_queue = self.updater.job_queue
        job_queue.run_once(self._report_callback, when=0, context=text)

    def _report_callback(self, callback_ctx):
        '''Runs in _updater thread'''
        text = callback_ctx.job.context
        self.report_unsafe(text)

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
