import os
import logging

class Config:
    DEFAULT_LISTEN_PORT = 8888
    DEFAULT_RTMP_PORT = 1935

    _PREFIX = 'BALTHIFY_'
    
    _get = lambda key: os.environ['BALTHIFY_' + key]
    _get_or_none = lambda key: os.environ.get('BALTHIFY_' + key)

    auth_path = _get('AUTH_PATH')
    listen_port = int(_get_or_none('LISTEN_PORT') or DEFAULT_LISTEN_PORT)
    
    chat_id = _get('CHAT_ID')
    admin_id = _get('ADMIN_ID')
    tg_token = _get('TOKEN')
    
    db_uri = _get('DB_URI')
    
    ingress_app = _get('APP_INGRESS')
    egress_app = _get('APP_EGRESS')
    rtmp_port = int(_get_or_none('RTMP_PORT') or DEFAULT_RTMP_PORT)
    rtmp_addr = _get('RTMP_ADDR')
    
    redirect_template = 'rtmp://127.0.0.1:{}/{{}}/{{}}'.format(rtmp_port)
    access_template = 'rtmp://{}:{}/{{}}/{{}}'.format(rtmp_addr, rtmp_port)
    
    loglevel = getattr(logging, _get_or_none('LOGLEVEL') or 'DEBUG')
