from uuid import UUID
from sqlalchemy.orm import Session
from rejesha_green.models.registration_payment import RegistrationPayment, PaymentStatus

class RegistrationPaymentRepository:
    def __init__(self, db: Session): self.db = db
    def create(self, payment: RegistrationPayment): self.db.add(payment); self.db.commit(); self.db.refresh(payment); return payment
    def get(self, payment_id: UUID): return self.db.query(RegistrationPayment).filter(RegistrationPayment.payment_id == payment_id).first()
    def get_by_checkout_id(self, checkout_request_id: str): 
        return self.db.query(RegistrationPayment).filter(RegistrationPayment.checkout_request_id == checkout_request_id).first()
    def get_pending_by_member(self, member_id: UUID): 
        return self.db.query(RegistrationPayment).filter(RegistrationPayment.member_id == member_id, RegistrationPayment.status == PaymentStatus.PENDING).first()
    def update(self, payment: RegistrationPayment): self.db.commit(); self.db.refresh(payment); return payment

registration_payment_repository = RegistrationPaymentRepository