from sqlalchemy import Column, MetaData
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
Base = declarative_base(metadata=metadata)

class ScheduledStream(Base):
    __tablename__ = 'ScheduledStream'
    ingress_app = Column(String, nullable=False)
    ingress_id = Column(String(32), primary_key=True)
    egress_app = Column(String, nullable=False)
    egress_id = Column(String(32), nullable=False)
    start_time = Column(DateTime, nullable=False)
