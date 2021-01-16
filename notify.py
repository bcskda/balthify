'''
Bot's notification feature
'''
from telegram.ext import Updater

class SafeNotifier:
    '''Lightweight thread-safe notifier impl'''
    def __init__(self, updater: Updater, chat_id):
        self.updater = updater
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

class NiceNotifier(SafeNotifier):
    '''Lightweight thread-safe notifier. Holds no ownership.'''
    def report_connect(self, addr, app):
        mesg = '\n'.join([
            'Connect',
            '',
            f'addr={addr}',
            f'app={app}',
        ])
        self.report(mesg)

    def report_publish(self, app, name):
        mesg = '\n'.join([
            'Publish',
            '',
            f'app={app}',
            f'name={name}',
        ])
        self.report(mesg)

    def report_schedule(self, title, comment, url, start):
        mesg = '\n'.join([
            'Schedule',
            '',
            f'Title: {title}',
            f'Start: {start}',
            f'Link: {url}',
            f'Description: {comment}'
        ])
        self.report(mesg)
