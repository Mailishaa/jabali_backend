import uuid
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from rejesha_green.models.user import UserRole
from rejesha_green.models.registration_payment import RegistrationPayment, PaymentStatus
from rejesha_green.repositories.user_repository import UserRepository
from rejesha_green.repositories.community_forest_association_repository import CommunityForestAssociationRepository
from rejesha_green.repositories.registration_payment_repository import RegistrationPaymentRepository
from rejesha_green.services.daraja_service import stk_push
from rejesha_green.services.sms_service import send_sms
from rejesha_green.services.user_service import generate_member_number

def initiate_registration_payment(db: Session, member_id: uuid.UUID, current_user):
    user_repo = UserRepository(db)
    cfa_repo = CommunityForestAssociationRepository(db)
    payment_repo = RegistrationPaymentRepository(db)
    official_id = uuid.UUID(current_user["sub"])
    official = user_repo.get_user(official_id)
    if not official or official.role != UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL: raise HTTPException(403, "Only a Community Forest Association Official can initiate registration payments")
    member = user_repo.get_user(member_id)
    if not member: raise HTTPException(404, "Member not found")
    if member.role != UserRole.MEMBER: raise HTTPException(400, "User is not a member")
    if member.community_forest_association_id != official.community_forest_association_id: raise HTTPException(403, "You cannot initiate payment for a member outside your Community Forest Association")
    cfa = cfa_repo.get(member.community_forest_association_id)
    if not cfa: raise HTTPException(404, "Community Forest Association not found")
    if member.membership_number: raise HTTPException(400, "Member is already registered")
    if cfa.registration_fee is None or cfa.registration_fee <= 0: raise HTTPException(400, "Invalid Community Forest Association registration fee")
    pending = payment_repo.get_pending_by_member(member_id)
    if pending: return {"message": "A registration payment is already pending", "payment_id": str(pending.payment_id), "checkout_request_id": pending.checkout_request_id, "amount": pending.amount, "phone": pending.phone}
    payment = payment_repo.create(RegistrationPayment(member_id=member.user_id, community_forest_association_id=cfa.community_forest_association_id, amount=cfa.registration_fee, phone=member.phone, status=PaymentStatus.PENDING))
    try: result = stk_push(phone=member.phone, amount=int(cfa.registration_fee))
    except Exception as exc:
        payment.status = PaymentStatus.FAILED; payment_repo.update(payment)
        raise HTTPException(502, "Failed to initiate M-Pesa payment") from exc
    if not result or str(result.get("ResponseCode", "0")) != "0":
        payment.status = PaymentStatus.FAILED; payment_repo.update(payment)
        raise HTTPException(502, result.get("ResponseDescription", "Daraja payment initiation failed"))
    checkout_id = result.get("CheckoutRequestID")
    if not checkout_id:
        payment.status = PaymentStatus.FAILED; payment_repo.update(payment)
        raise HTTPException(502, "Daraja did not return a CheckoutRequestID")
    payment.checkout_request_id = checkout_id
    payment.merchant_request_id = result.get("MerchantRequestID")
    payment_repo.update(payment)
    return {"message": "Registration payment initiated", "payment_id": str(payment.payment_id), "member_id": str(member.user_id), "amount": payment.amount, "phone": payment.phone, "checkout_request_id": payment.checkout_request_id, "merchant_request_id": payment.merchant_request_id}

def process_registration_payment(db: Session, payload: dict):
    payment_repo = RegistrationPaymentRepository(db)
    callback = payload.get("Body", {}).get("stkCallback", {})
    checkout_request_id = callback.get("CheckoutRequestID")
    if not checkout_request_id: raise HTTPException(400, "CheckoutRequestID missing")
    payment = payment_repo.get_by_checkout_id(checkout_request_id)
    if not payment: raise HTTPException(404, "Payment not found")
    result_code = callback.get("ResultCode")
    if result_code == 0:
        items = {item.get("Name"): item.get("Value") for item in callback.get("CallbackMetadata", {}).get("Item", [])}
        payment.status = PaymentStatus.PAID
        payment.mpesa_receipt = items.get("MpesaReceiptNumber")
        payment.paid_at = datetime.utcnow()
        payment_repo.update(payment)
        member = payment.member
        if not member.membership_number: member.membership_number = generate_member_number()
        db.commit()
        try: send_sms(member.phone, f"Registration successful. Your membership number is {member.membership_number}")
        except Exception: pass
        return {"message": "Registration payment completed", "payment_id": str(payment.payment_id), "membership_number": member.membership_number}
    payment.status = PaymentStatus.FAILED
    payment_repo.update(payment)
    return {"message": "Registration payment failed", "payment_id": str(payment.payment_id), "result_code": result_code}