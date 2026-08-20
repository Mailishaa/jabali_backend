import uuid
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from rejesha_green.models.user import User, CFA, RegistrationPayment, UserRole, PaymentStatus
from rejesha_green.repositories.user_repository import UserRepository
from rejesha_green.security import hash_password
from rejesha_green.services.daraja_service import stk_push
from rejesha_green.services.sms_service import send_sms




def generate_member_number():
   return f"JAB-{uuid.uuid4().hex[:8].upper()}"




def create_user(db: Session, data):
   repo = UserRepository(db)
   if repo.get_by_national_id(data.national_id):
       raise HTTPException(400, "National ID already exists")
   if repo.get_by_phone(data.phone):
       raise HTTPException(400, "Phone number already exists")
   if data.email and repo.get_by_email(data.email):
       raise HTTPException(400, "Email already exists")
   return repo.create_user(User(national_id=data.national_id, first_name=data.first_name, last_name=data.last_name, phone=data.phone, email=data.email, password_hash=hash_password(data.password) if data.password else None, role=data.role, user_group=data.user_group, block_name=data.block_name))




def register_kfs_official(db: Session, data, current_user):
   repo = UserRepository(db)
   if data.role != UserRole.KFS_OFFICIAL:
       raise HTTPException(400, "Role must be kfs_official")
   if not data.password:
       raise HTTPException(400, "Password is required")
   if repo.get_by_national_id(data.national_id):
       raise HTTPException(400, "National ID already exists")
   if repo.get_by_phone(data.phone):
       raise HTTPException(400, "Phone already exists")
   if data.email and repo.get_by_email(data.email):
       raise HTTPException(400, "Email already exists")
   return repo.create_user(User(national_id=data.national_id, first_name=data.first_name, last_name=data.last_name, phone=data.phone, email=data.email, password_hash=hash_password(data.password), role=UserRole.KFS_OFFICIAL, registered_by=uuid.UUID(current_user["sub"])))




def register_cfa_official(db: Session, kfs_id: uuid.UUID, data, current_user):
   repo = UserRepository(db)
   if uuid.UUID(current_user["sub"]) != kfs_id:
       raise HTTPException(403, "Unauthorized KFS account")
   kfs = repo.get_user(kfs_id)
   if not kfs or kfs.role != UserRole.KFS_OFFICIAL:
       raise HTTPException(403, "Invalid KFS official")
   if repo.get_cfa_by_name(data.cfa_name):
       raise HTTPException(400, "CFA already exists")
   if repo.get_by_national_id(data.national_id):
       raise HTTPException(400, "National ID already exists")
   if repo.get_by_phone(data.phone):
       raise HTTPException(400, "Phone already exists")
   if data.email and repo.get_by_email(data.email):
       raise HTTPException(400, "Email already exists")
   cfa = CFA(cfa_name=data.cfa_name, kfs_official_id=kfs_id, registration_fee=data.registration_fee)
   repo.create_cfa(cfa)
   return repo.create_user(User(national_id=data.national_id, first_name=data.first_name,
   last_name=data.last_name, phone=data.phone, email=data.email, password_hash=hash_password(data.password), role=UserRole.CFA_OFFICIAL, registered_by=kfs_id, cfa_id=cfa.cfa_id))




def register_member(db: Session, cfa_id: uuid.UUID, data, current_user):
   repo = UserRepository(db)
   cfa_official_id = uuid.UUID(current_user["sub"])
   cfa_official = repo.get_user(cfa_official_id)
   if not cfa_official:
       raise HTTPException(404, "CFA official not found")
   if cfa_official.role != UserRole.CFA_OFFICIAL:
       raise HTTPException(403, "Invalid CFA official")
   if cfa_official.cfa_id != cfa_id:
       raise HTTPException(403, "You cannot register members outside your CFA")
   cfa = repo.get_cfa(cfa_id)
   if not cfa:
       raise HTTPException(404, "CFA not found")
   if data.role != UserRole.MEMBER:
       raise HTTPException(400, "Role must be member")
   if repo.get_by_national_id(data.national_id):
       raise HTTPException(400, "National ID already exists")
   if repo.get_by_phone(data.phone):
       raise HTTPException(400, "Phone number already exists")
   if data.email and repo.get_by_email(data.email):
       raise HTTPException(400, "Email already exists")
   return repo.create_user(User(national_id=data.national_id, first_name=data.first_name, last_name=data.last_name, phone=data.phone, email=data.email, password_hash=None, role=UserRole.MEMBER, user_group=data.user_group, cfa_id=cfa_id, block_name=data.block_name, registered_by=cfa_official_id, membership_number=None))




def initiate_registration_payment(db: Session, member_id: uuid.UUID, current_user):
   repo = UserRepository(db)
   cfa_official_id = uuid.UUID(current_user["sub"])
   cfa_official = repo.get_user(cfa_official_id)
   if not cfa_official:
       raise HTTPException(404, "CFA official not found")
   if cfa_official.role != UserRole.CFA_OFFICIAL:
       raise HTTPException(403, "Only a CFA official can initiate registration payment")
   member = repo.get_user(member_id)
   if not member:
       raise HTTPException(404, "Member not found")
   if member.role != UserRole.MEMBER:
       raise HTTPException(400, "User is not a member")
   if member.cfa_id != cfa_official.cfa_id:
       raise HTTPException(403, "You cannot initiate payment for a member outside your CFA")
   cfa = repo.get_cfa(member.cfa_id)
   if not cfa:
       raise HTTPException(404, "CFA not found")
   if member.membership_number:
       raise HTTPException(400, "Member is already registered")
   if cfa.registration_fee is None or float(cfa.registration_fee) <= 0:
       raise HTTPException(400, "Invalid CFA registration fee")
   if not member.phone:
       raise HTTPException(400, "Member does not have a phone number")
   pending = repo.get_pending_payment(member_id)
   if pending:
       return {"message": "A registration payment is already pending", "payment_id": str(pending.payment_id), "checkout_request_id": pending.checkout_request_id, "amount": pending.amount, "phone": pending.phone}
   payment = repo.create_payment(RegistrationPayment(member_id=member.user_id, cfa_id=cfa.cfa_id, amount=cfa.registration_fee, phone=member.phone, status=PaymentStatus.PENDING))
   try:
       result = stk_push(phone=member.phone, amount=int(cfa.registration_fee))
   except Exception as exc:
       payment.status = PaymentStatus.FAILED
       repo.update_payment(payment)
       raise HTTPException(502, "Failed to initiate M-Pesa payment") from exc
   if not result:
       payment.status = PaymentStatus.FAILED
       repo.update_payment(payment)
       raise HTTPException(502, "Empty response received from Daraja")
   response_code = result.get("ResponseCode")
   if response_code is not None and str(response_code) != "0":
       payment.status = PaymentStatus.FAILED
       repo.update_payment(payment)
       raise HTTPException(502, result.get("ResponseDescription", "Daraja rejected the STK Push request"))
   checkout_request_id = result.get("CheckoutRequestID")
   merchant_request_id = result.get("MerchantRequestID")
   if not checkout_request_id:
       payment.status = PaymentStatus.FAILED
       repo.update_payment(payment)
       raise HTTPException(502, "Daraja did not return a CheckoutRequestID")
   payment.checkout_request_id = checkout_request_id
   payment.merchant_request_id = merchant_request_id
   repo.update_payment(payment)
   return {"message": "Registration payment initiated", "payment_id": str(payment.payment_id), "member_id": str(member.user_id), "amount": cfa.registration_fee, "phone": member.phone, "checkout_request_id": checkout_request_id, "merchant_request_id": merchant_request_id}




def process_registration_payment(db: Session, payload: dict):
   repo = UserRepository(db)
   callback = payload.get("Body", {}).get("stkCallback", {})
   checkout_id = callback.get("CheckoutRequestID")
   if not checkout_id:
       raise HTTPException(400, "Invalid Daraja callback")
   payment = repo.get_payment_by_checkout_id(checkout_id)
   if not payment:
       raise HTTPException(404, "Payment not found")
   if payment.status == PaymentStatus.PAID:
       return {"message": "Payment already processed"}
   try:
       result_code = int(callback.get("ResultCode"))
   except (TypeError, ValueError):
       payment.status = PaymentStatus.FAILED
       repo.update_payment(payment)
       return {"message": "Invalid payment callback"}
   if result_code != 0:
       payment.status = PaymentStatus.FAILED
       repo.update_payment(payment)
       return {"message": "Registration payment failed", "result_code": result_code}
   metadata = callback.get("CallbackMetadata", {}).get("Item", [])


   def get_metadata_value(name):
       return next((item.get("Value") for item in metadata if item.get("Name") == name), None)


   receipt = get_metadata_value("MpesaReceiptNumber")
   callback_amount = get_metadata_value("Amount")
   callback_phone = get_metadata_value("PhoneNumber")
   transaction_date = get_metadata_value("TransactionDate")


   if not receipt:
       raise HTTPException(400, "Invalid successful payment callback")


   member = repo.get_user(payment.member_id)
   if not member:
       raise HTTPException(404, "Member not found")


   if callback_amount is not None:
       try:
           if float(callback_amount) != float(payment.amount):
               payment.status = PaymentStatus.FAILED
               repo.update_payment(payment)
               return {"message": "Payment amount mismatch"}
       except (TypeError, ValueError):
           payment.status = PaymentStatus.FAILED
           repo.update_payment(payment)
           return {"message": "Invalid payment amount"}


   if callback_phone is not None:
       expected_phone = str(payment.phone).replace("+", "")
       received_phone = str(callback_phone).replace("+", "")
       if len(expected_phone) >= 9 and len(received_phone) >= 9 and expected_phone[-9:] != received_phone[-9:]:
           payment.status = PaymentStatus.FAILED
           repo.update_payment(payment)
           return {"message": "Payment phone mismatch"}


   payment.status = PaymentStatus.PAID
   payment.mpesa_receipt = receipt
   payment.paid_at = datetime()


   if not member.membership_number:
       member.membership_number = generate_member_number()


   repo.update_payment(payment)
   repo.update_user(member)


   sms_message = f"JABALI registration successful. Welcome {member.first_name}. Member number: {member.membership_number}. Registration fee paid: KES {payment.amount}. Your login email is {member.email}."


   try:
       sms_sent = send_sms(phone=member.phone, message=sms_message)
   except Exception:
       sms_sent = False


   return {"message": "Payment successful", "member_id": str(member.user_id), "member_number": member.membership_number, "mpesa_receipt": receipt, "amount": payment.amount, "transaction_date": transaction_date, "sms": "sent" if sms_sent else "failed"}




def update_user(db: Session, user_id: uuid.UUID, data):
   repo = UserRepository(db)
   user = repo.get_user(user_id)
   if not user:
       raise HTTPException(404, "User not found")
   for field, value in data.model_dump(exclude_unset=True).items():
       setattr(user, field, value)
   return repo.update_user(user)




def delete_user(db: Session, user_id: uuid.UUID):
   repo = UserRepository(db)
   user = repo.get_user(user_id)
   if not user:
       raise HTTPException(404, "User not found")
   repo.delete_user(user)
   return {"message": "User deleted successfully"}




def update_cfa(db: Session, cfa_id: uuid.UUID, data, current_user):
   repo = UserRepository(db)
   cfa = repo.get_cfa(cfa_id)
   if not cfa:
       raise HTTPException(404, "CFA not found")
   if cfa.kfs_official_id != uuid.UUID(current_user["sub"]):
       raise HTTPException(403, "You do not manage this CFA")
   for field, value in data.model_dump(exclude_unset=True).items():
       setattr(cfa, field, value)
   return repo.update_cfa(cfa)




def delete_cfa(db: Session, cfa_id: uuid.UUID, current_user):
   repo = UserRepository(db)
   cfa = repo.get_cfa(cfa_id)
   if not cfa:
       raise HTTPException(404, "CFA not found")
   if cfa.kfs_official_id != uuid.UUID(current_user["sub"]):
       raise HTTPException(403, "You do not manage this CFA")
   repo.delete_cfa(cfa)
   return {"message": "CFA deleted successfully"}
