import base64
import math
import os
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from balthify2.common.models import (
    RoutingRecord,
    RoutingRecordUserConfigurable,
    RoutingRecordOrm
)
from balthify2.schedule.sessions import Sessions


router = APIRouter()


def random_id(length: int):
    urandom_bytes_cnt = math.ceil(3 / 4 * length)
    urandom_bytes = os.urandom(urandom_bytes_cnt)
    rnd = base64.b64encode(urandom_bytes, altchars=b'_-').decode('utf-8')
    return rnd[:length]


@router.get('/lookup')
async def get_record(ingress_app: str, ingress_id: str, timestamp: datetime):
    async with Sessions.make() as session:
        query = select(RoutingRecordOrm).filter(
            RoutingRecordOrm.ingress_app == ingress_app,
            RoutingRecordOrm.ingress_id == ingress_id,
            RoutingRecordOrm.start_time <= timestamp,
            timestamp < RoutingRecordOrm.end_time
        )
        result = await session.execute(query)
        records_orm = result.scalars().all()

        if len(records_orm) == 1:
            return RoutingRecord.from_orm(records_orm[0])
        elif len(records_orm) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Overlapping routing records')


@router.post('/')
async def post_record(record: RoutingRecordUserConfigurable):
    async with Sessions.make() as session:
        ingress_id = random_id(32)
        egress_id = random_id(32)
        record_orm = RoutingRecordOrm(
            ingress_id=ingress_id,
            egress_id=egress_id,
            **record.dict()
        )
        session.add(record_orm)
        await session.commit()
        return RoutingRecord.from_orm(record_orm)
