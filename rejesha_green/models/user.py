
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Numeric, String
import enum, uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    KENYA_FOREST_SERVICE_OFFICIAL = "kenya_forest_service_official"
    COMMUNITY_FOREST_ASSOCIATION_OFFICIAL = "community_forest_association_official"
    MEMBER = "member"

class UserGroup(str, enum.Enum):
    BEEKEEPING = "beekeeping"
    TREE_PLANTING = "tree_planting"
    FIREWOOD_COLLECTION = "firewood_collection"
    ECO_TOURISM = "eco_tourism"

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    national_id = Column(String(20), unique=True, nullable=False, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(Enum(UserRole, values_callable=lambda x: [e.value for e in x], name="user_role"), nullable=False)
    membership_number = Column(String(50), unique=True, nullable=True, index=True)
    user_group = Column(Enum(UserGroup, values_callable=lambda x: [e.value for e in x], name="user_group"), nullable=True)
    registered_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    community_forest_association_id = Column(UUID(as_uuid=True), ForeignKey("community_forest_associations.community_forest_association_id"), nullable=True)
    block_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    community_forest_association = relationship("CommunityForestAssociation", foreign_keys=[community_forest_association_id], back_populates="members")
    payments = relationship("RegistrationPayment", foreign_keys="RegistrationPayment.member_id", back_populates="member")
    registered_by_user = relationship("User", remote_side=[user_id], foreign_keys=[registered_by], back_populates="registered_users")
    registered_users = relationship("User", foreign_keys=[registered_by], back_populates="registered_by_user")
    managed_community_forest_associations = relationship("CommunityForestAssociation", foreign_keys="CommunityForestAssociation.kenya_forest_service_official_id", back_populates="kenya_forest_service_official")ure/permit