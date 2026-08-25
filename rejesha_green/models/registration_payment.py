import enum, uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"

class RegistrationPayment(Base):
    __tablename__ = "registration_payments"
    payment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    community_forest_association_id = Column(UUID(as_uuid=True), ForeignKey("community_forest_associations.community_forest_association_id"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    phone = Column(String(20), nullable=False)
    checkout_request_id = Column(String(100), unique=True, nullable=True, index=True)
    merchant_request_id = Column(String(100), nullable=True)
    mpesa_receipt = Column(String(100), nullable=True, index=True)
    status = Column(Enum(PaymentStatus, values_callable=lambda x: [e.value for e in x], name="payment_status"), default=PaymentStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    paid_at = Column(DateTime, nullable=True)
    member = relationship("User", foreign_keys=[member_id], back_populates="payments")
    community_forest_association = relationship("CommunityForestAssociation", foreign_keys=[community_forest_association_id], back_populates="payments")