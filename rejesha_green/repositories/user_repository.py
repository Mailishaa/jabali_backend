from uuid import UUID
from sqlalchemy.orm import Session
from rejesha_green.models.user import User, CFA, RegistrationPayment, PaymentStatus




class UserRepository:
   def __init__(self, db: Session):
       self.db = db


   def create_user(self, user: User):
       self.db.add(user); self.db.commit(); self.db.refresh(user); return user


   def get_user(self, user_id: UUID):
       return self.db.query(User).filter(User.user_id == user_id).first()


   def get_all_users(self, skip=0, limit=100):
       return self.db.query(User).offset(skip).limit(limit).all()


   def get_by_phone(self, phone: str):
       return self.db.query(User).filter(User.phone == phone).first()


   def get_by_national_id(self, national_id: str):
       return self.db.query(User).filter(User.national_id == national_id).first()


   def get_by_email(self, email: str):
       return self.db.query(User).filter(User.email == email).first()


   def update_user(self, user: User):
       self.db.commit(); self.db.refresh(user); return user


   def delete_user(self, user: User):
       self.db.delete(user); self.db.commit()


   def create_cfa(self, cfa: CFA):
       self.db.add(cfa); self.db.commit(); self.db.refresh(cfa); return cfa


   def get_cfa(self, cfa_id: UUID):
       return self.db.query(CFA).filter(CFA.cfa_id == cfa_id).first()


   def get_all_cfas(self, skip=0, limit=100):
       return self.db.query(CFA).offset(skip).limit(limit).all()


   def get_cfa_by_name(self, cfa_name: str):
       return self.db.query(CFA).filter(CFA.cfa_name == cfa_name).first()


   def update_cfa(self, cfa: CFA):
       self.db.commit(); self.db.refresh(cfa); return cfa


   def delete_cfa(self, cfa: CFA):
       self.db.delete(cfa); self.db.commit()


   def create_payment(self, payment: RegistrationPayment):
       self.db.add(payment); self.db.commit(); self.db.refresh(payment); return payment


   def get_payment(self, payment_id: UUID):
       return self.db.query(RegistrationPayment).filter(RegistrationPayment.payment_id == payment_id).first()


   def get_payment_by_checkout_id(self, checkout_request_id: str):
       return self.db.query(RegistrationPayment).filter(
           RegistrationPayment.checkout_request_id == checkout_request_id
       ).first()


   def get_pending_payment(self, member_id: UUID):
       return self.db.query(RegistrationPayment).filter(
           RegistrationPayment.member_id == member_id,
           RegistrationPayment.status == PaymentStatus.PENDING
       ).first()


   def update_payment(self, payment: RegistrationPayment):
       self.db.commit(); self.db.refresh(payment); return payment
