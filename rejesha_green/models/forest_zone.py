from sqlalchemy import Column, String, Boolean, Float
from database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID


class ForestZone(Base):
    __tablename__ = "forest_zones"

    zone_id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    cfa_name = Column(String(100),nullable=False)
    block_name = Column(String(100), nullable=False)
    resource_type = Column(String(100),nullable=False)
    is_available = Column(Boolean,default=True,nullable=False)
    price = Column(Float,nullable=False)