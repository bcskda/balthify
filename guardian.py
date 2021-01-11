'''
Decides to accept/reject RTMP streams
'''
from logs import get_logger

class Guardian:
    def __init__(self):
        self.logger = get_logger('guardian')

    def check_publish(self, addr, app, name):
        '''True = accept publish, False = reject'''
        self.logger.debug('publish: addr=%s app=%s name=%s', addr, app, name)
        self.logger.warning('publish: unconditional accept')
        return True

    def check_connect(self, addr, app):
        '''True = accept connect, False = reject'''
        self.logger.debug('connect: addr=%s app=%s', addr, app)
        self.logger.warning('connect: unconditional accept')
        return True
