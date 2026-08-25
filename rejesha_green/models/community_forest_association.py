import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

class CommunityForestAssociation(Base):
    __tablename__ = "community_forest_associations"
    community_forest_association_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    community_forest_association_name = Column(String(150), unique=True, nullable=False, index=True)
    kenya_forest_service_official_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", use_alter=True, name="fk_cfa_kfs_official"), nullable=False)
    registration_fee = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    kenya_forest_service_official = relationship("User", foreign_keys=[kenya_forest_service_official_id], back_populates="managed_community_forest_associations")
    members = relationship("User", foreign_keys="User.community_forest_association_id", back_populates="community_forest_association")
    payments = relationship("RegistrationPayment", foreign_keys="RegistrationPayment.community_forest_association_id", back_populates="community_forest_association")