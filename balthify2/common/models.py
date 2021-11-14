import typing as tp
from datetime import datetime

from pydantic import BaseModel, constr, validator
from sqlalchemy import Column, ForeignKey, MetaData, Sequence
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base


metadata = MetaData()
Base = declarative_base(metadata=metadata)


class RoutingRecordOrm(Base):
    __tablename__ = 'RoutingRecord'
    id = Column(Integer, Sequence('routing_id_seq'),
                        primary_key=True)
    ingress_app = Column(String(32), nullable=False)
    ingress_id = Column(String(32), nullable=False)
    egress_app = Column(String(32), nullable=False)
    egress_id = Column(String(32), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(300), nullable=False)


class RoutingRecord(BaseModel):
    id: tp.Optional[int]
    ingress_app: constr(max_length=32)
    ingress_id: constr(max_length=32)
    egress_app: constr(max_length=32)
    egress_id: constr(max_length=32)
    start_time: datetime
    end_time: datetime
    title: constr(max_length=100)
    description: constr(max_length=300)

    class Config:
        orm_mode = True

    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        assert v > values['start_time']
        return v

    @validator('title')
    def title_non_empty_oneliner(cls, v):
        assert len(v) > 0 and '\n' not in v
        return v


class RoutingRecordByIdsReq(BaseModel):
    ingress_app: constr(max_length=32)
    ingress_id: constr(max_length=32)
    timestamp: datetime
