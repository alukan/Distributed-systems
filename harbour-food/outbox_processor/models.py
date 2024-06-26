from db import Base
from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP, func, Float

class Outbox(Base):
    __tablename__ = 'outbox'
    id = Column(Integer, primary_key=True, autoincrement=True)
    aggregate_id = Column(Integer, nullable=False)
    aggregate_type = Column(String(255), nullable=False)
    payload = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    processed_at = Column(TIMESTAMP, nullable=True)