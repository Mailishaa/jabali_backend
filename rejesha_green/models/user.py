import enum
import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class UserRole(str, enum.Enum):
   SUPER_ADMIN = "super_admin"
   KFS_OFFICIAL = "kfs_official"
   CFA_OFFICIAL = "cfa_official"
   MEMBER = "member"


class UserGroup(str, enum.Enum):
   BEEKEEPING = "beekeeping"
   TREE_PLANTING = "tree_planting"
   FIREWOOD_COLLECTION = "firewood_collection"
   ECO_TOURISM = "eco_tourism"


class PaymentStatus(str, enum.Enum):
   PENDING = "pending"
   PAID = "paid"
   FAILED = "failed"


class CFA(Base):
   __tablename__ = "cfas"
   cfa_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
   cfa_name = Column(String(150), unique=True, nullable=False)
   kfs_official_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
   registration_fee = Column(Numeric(10, 2), nullable=False)
   is_active = Column(Boolean, default=True, nullable=False)
   created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
   updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(Base):
   __tablename__ = "users"
   user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
   national_id = Column(String(20), unique=True, nullable=False, index=True)
   first_name = Column(String(50), nullable=False)
   last_name = Column(String(50), nullable=False)
   phone = Column(String(20), unique=True, nullable=False, index=True)
   email = Column(String(255), unique=True, nullable=True)
   password_hash = Column(String(255), nullable=True)
   role = Column(Enum(UserRole), nullable=False, index=True)
   membership_number = Column(String(50), unique=True, nullable=True, index=True)
   user_group = Column(Enum(UserGroup), nullable=True)
   registered_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
   cfa_id = Column(UUID(as_uuid=True), ForeignKey("cfas.cfa_id"), nullable=True, index=True)
   block_name = Column(String(100), nullable=True)
   is_active = Column(Boolean, default=True, nullable=False)
   created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
   updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class RegistrationPayment(Base):
   __tablename__ = "registration_payments"
   payment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
   member_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
   cfa_id = Column(UUID(as_uuid=True), ForeignKey("cfas.cfa_id"), nullable=False, index=True)
   amount = Column(Numeric(10, 2), nullable=False)
   phone = Column(String(20), nullable=False)
   checkout_request_id = Column(String(100), unique=True, nullable=True, index=True)
   merchant_request_id = Column(String(100), nullable=True)
   mpesa_receipt = Column(String(100), nullable=True)
   status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
   created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
   paid_at = Column(DateTime, nullable=True)
