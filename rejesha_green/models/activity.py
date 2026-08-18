import uuid
import enum
from datetime import datetime, date

from sqlalchemy import Column, String, Date, Text, Integer, DateTime, Enum, ForeignKey
from database import Base
from sqlalchemy.dialects.postgresql import UUID


class UserGroup(str, enum.Enum):
    TREE_PLANTING = "tree_planting"
    ECO_TOURISM = "eco_tourism"
    FOREST_CLEANING = "forest_cleaning"
    FOREST_PATROL = "forest_patrol"


class Activity(Base):
    __tablename__ = "activities"

    activity_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_by = Column(String(36), nullable=False)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("forest_zones.zone_id"), nullable=False)
    activity_name = Column(String(100), nullable=False)
    scheduled_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    user_group = Column(Enum(UserGroup), nullable=True)
    expected_attendees = Column(Integer, nullable=False)
    actual_attendees = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime, nullable=False)