from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from rejesha_green.models.registration_payment import PaymentStatus

class RegistrationPaymentCreate(BaseModel):
    member_id: UUID
    community_forest_association_id: UUID
    amount: Decimal
    phone: str

class RegistrationPaymentResponse(BaseModel):
    payment_id: UUID
    member_id: UUID
    community_forest_association_id: UUID
    amount: Decimal
    phone: str
    status: PaymentStatus
    checkout_request_id: str | None = None
    merchant_request_id: str | None = None
    mpesa_receipt: str | None = None
    created_at: datetime
    paid_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)