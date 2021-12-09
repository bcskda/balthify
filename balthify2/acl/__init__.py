import json
from datetime import datetime

from fastapi import APIRouter, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import url_concat

from balthify2.common.models import RoutingRecord
from balthify2.acl.config import Config


router = APIRouter()


@router.post('/on_connect')
async def on_connect(
    call: str = Form(...),
    addr: str = Form(...),
    app: str = Form(...),
    name: str = Form(...),
):
    assert call == 'connect'
    return {'message': 'ok'}


@router.post('/on_publish')
async def on_publish(
    call: str = Form(...),
    addr: str = Form(...),
    app: str = Form(...),
    name: str = Form(...),
):
    assert call == 'publish'
    config = Config()

    request = {
        'ingress_app': app,
        'ingress_id': name,
        'timestamp': datetime.now(),
    }
    client = AsyncHTTPClient()
    response = await client.fetch(
        url_concat(config.lookup_url, request),
        raise_error=False
    )

    if response.code == status.HTTP_200_OK:
        response = RoutingRecord(**json.loads(response.body))
        redirect_to = f'rtmp://{config.redirect_domain}/{response.egress_app}/{response.egress_id}'
        return RedirectResponse(redirect_to)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'Schedule status_code={response.code}')
