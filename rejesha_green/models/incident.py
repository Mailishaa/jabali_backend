from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import func

import enum
import uuid
from sqlalchemy import Column, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID


class ActivityType(str, enum.Enum):
    Charcoal_Burning = "Charcoal burning"
    Logging = "Logging"
    Poaching = "Poaching"
    Others = "Others"


class IncidentReport(Base):
    __tablename__ = "incidents_report"

    incident_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("forest_zones.zone_id"), nullable=False)
    incident_type = Column(Enum(ActivityType), nullable=False)
    reported_at = Column(DateTime, server_default=func.now(), nullable=False)