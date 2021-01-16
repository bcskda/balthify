from sqlalchemy import Column, ForeignKey, MetaData, Sequence
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
Base = declarative_base(metadata=metadata)

class RoutingRecord(Base):
    __tablename__ = 'RoutingRecord'
    routing_id = Column(Integer, Sequence('routing_id_seq'),
                        primary_key=True)
    ingress_app = Column(String, nullable=False)
    ingress_id = Column(String(32), nullable=False)
    egress_app = Column(String, nullable=False)
    egress_id = Column(String(32), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
