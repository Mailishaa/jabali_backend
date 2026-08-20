import uuid
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from rejesha_green.models.user import User,CommunityForestAssociation,RegistrationPayment,UserRole,PaymentStatus
from rejesha_green.repositories.user_repository import UserRepository
from rejesha_green.security import hash_password
from rejesha_green.services.daraja_service import stk_push
from rejesha_green.services.sms_service import send_sms

def generate_member_number(): return f"JAB-{uuid.uuid4().hex[:8].upper()}"

def validate_user(repo,data,require_password=False):
    if repo.get_by_national_id(data.national_id): raise HTTPException(400,"National ID already exists")
    if repo.get_by_phone(data.phone): raise HTTPException(400,"Phone number already exists")
    if data.email and repo.get_by_email(data.email): raise HTTPException(400,"Email already exists")
    if require_password and not data.password: raise HTTPException(400,"Password is required")

def create_user_record(data,role,registered_by=None,community_forest_association_id=None):
    return User(national_id=data.national_id,first_name=data.first_name,last_name=data.last_name,phone=data.phone,email=data.email if role!=UserRole.MEMBER else None,password_hash=hash_password(data.password) if role!=UserRole.MEMBER and data.password else None,role=role,user_group=data.user_group if role==UserRole.MEMBER else None,block_name=data.block_name if role==UserRole.MEMBER else None,registered_by=registered_by,community_forest_association_id=community_forest_association_id)

def create_user(db:Session,data):
    repo=UserRepository(db)
    role=data.role
    if not role: raise HTTPException(400,"User role is required")
    validate_user(repo,data,role!=UserRole.MEMBER)
    return repo.create_user(create_user_record(data,role,community_forest_association_id=data.community_forest_association_id))

def register_kenya_forest_service_official(db:Session,data,current_user):
    repo=UserRepository(db)
    validate_user(repo,data,True)
    admin_id=uuid.UUID(current_user["sub"])
    return repo.create_user(create_user_record(data,UserRole.KENYA_FOREST_SERVICE_OFFICIAL,registered_by=admin_id))

def register_community_forest_association_official(db:Session,data,current_user):
    repo=UserRepository(db)
    kenya_forest_service_official_id=uuid.UUID(current_user["sub"])
    kenya_forest_service_official=repo.get_user(kenya_forest_service_official_id)
    if not kenya_forest_service_official or kenya_forest_service_official.role!=UserRole.KENYA_FOREST_SERVICE_OFFICIAL: raise HTTPException(403,"Invalid Kenya Forest Service Official")
    if repo.get_community_forest_association_by_name(data.community_forest_association_name): raise HTTPException(400,"Community Forest Association already exists")
    validate_user(repo,data,True)
    community_forest_association=repo.create_community_forest_association(CommunityForestAssociation(community_forest_association_name=data.community_forest_association_name,kenya_forest_service_official_id=kenya_forest_service_official_id,registration_fee=data.registration_fee))
    user=User(national_id=data.national_id,first_name=data.first_name,last_name=data.last_name,phone=data.phone,email=data.email,password_hash=hash_password(data.password),role=UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL,registered_by=kenya_forest_service_official_id,community_forest_association_id=community_forest_association.community_forest_association_id)
    return repo.create_user(user)

def register_member(db:Session,data,current_user):
    repo=UserRepository(db)
    official_id=uuid.UUID(current_user["sub"])
    official=repo.get_user(official_id)
    if not official or official.role!=UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL: raise HTTPException(403,"Invalid Community Forest Association Official")
    if not official.community_forest_association_id: raise HTTPException(400,"Official is not assigned to a Community Forest Association")
    validate_user(repo,data)
    return repo.create_user(create_user_record(data,UserRole.MEMBER,registered_by=official_id,community_forest_association_id=official.community_forest_association_id))

def initiate_registration_payment(db:Session,member_id:uuid.UUID,current_user):
    repo=UserRepository(db)
    official_id=uuid.UUID(current_user["sub"])
    official=repo.get_user(official_id)
    if not official or official.role!=UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL: raise HTTPException(403,"Only a Community Forest Association Official can initiate registration payment")
    member=repo.get_user(member_id)
    if not member: raise HTTPException(404,"Member not found")
    if member.role!=UserRole.MEMBER: raise HTTPException(400,"User is not a member")
    if member.community_forest_association_id!=official.community_forest_association_id: raise HTTPException(403,"You cannot initiate payment for a member outside your Community Forest Association")
    community_forest_association=repo.get_community_forest_association(member.community_forest_association_id)
    if not community_forest_association: raise HTTPException(404,"Community Forest Association not found")
    if member.membership_number: raise HTTPException(400,"Member is already registered")
    if community_forest_association.registration_fee is None or float(community_forest_association.registration_fee)<=0: raise HTTPException(400,"Invalid Community Forest Association registration fee")
    if not member.phone: raise HTTPException(400,"Member does not have a phone number")
    pending=repo.get_pending_payment(member_id)
    if pending: return {"message":"A registration payment is already pending","payment_id":str(pending.payment_id),"checkout_request_id":pending.checkout_request_id,"amount":pending.amount,"phone":pending.phone}
    payment=repo.create_payment(RegistrationPayment(member_id=member.user_id,community_forest_association_id=community_forest_association.community_forest_association_id,amount=community_forest_association.registration_fee,phone=member.phone,status=PaymentStatus.PENDING))
    try: result=stk_push(phone=member.phone,amount=int(community_forest_association.registration_fee))
    except Exception as exc:
        payment.status=PaymentStatus.FAILED;repo.update_payment(payment);raise HTTPException(502,"Failed to initiate M-Pesa payment") from exc
    if not result: payment.status=PaymentStatus.FAILED;repo.update_payment(payment);raise HTTPException(502,"Empty response received from Daraja")
    if result.get("ResponseCode") is not None and str(result.get("ResponseCode"))!="0":
        payment.status=PaymentStatus.FAILED;repo.update_payment(payment);raise HTTPException(502,result.get("ResponseDescription","Daraja rejected the STK Push request"))
    checkout_request_id=result.get("CheckoutRequestID")
    if not checkout_request_id: payment.status=PaymentStatus.FAILED;repo.update_payment(payment);raise HTTPException(502,"Daraja did not return a CheckoutRequestID")
    payment.checkout_request_id=checkout_request_id
    payment.merchant_request_id=result.get("MerchantRequestID")
    repo.update_payment(payment)
    return {"message":"Registration payment initiated","payment_id":str(payment.payment_id),"member_id":str(member.user_id),"amount":community_forest_association.registration_fee,"phone":member.phone,"checkout_request_id":checkout_request_id,"merchant_request_id":payment.merchant_request_id}

def process_registration_payment(db:Session,payload:dict):
    repo=UserRepository(db)
    callback=payload.get("Body",{}).get("stkCallback",{})
    checkout_id=callback.get("CheckoutRequestID")
    if not checkout_id: raise HTTPException(400,"Invalid Daraja callback")
    payment=repo.get_payment_by_checkout_id(checkout_id)
    if not payment: raise HTTPException(404,"Payment not found")
    if payment.status==PaymentStatus.PAID: return {"message":"Payment already processed"}
    try: result_code=int(callback.get("ResultCode"))
    except (TypeError,ValueError):
        payment.status=PaymentStatus.FAILED;repo.update_payment(payment);return {"message":"Invalid payment callback"}
    if result_code!=0:
        payment.status=PaymentStatus.FAILED;repo.update_payment(payment);return {"message":"Registration payment failed","result_code":result_code}
    metadata=callback.get("CallbackMetadata",{}).get("Item",[])
    def metadata_value(name): return next((item.get("Value") for item in metadata if item.get("Name")==name),None)
    receipt=metadata_value("MpesaReceiptNumber")
    callback_amount=metadata_value("Amount")
    callback_phone=metadata_value("PhoneNumber")
    transaction_date=metadata_value("TransactionDate")
    if not receipt: raise HTTPException(400,"Invalid successful payment callback")
    member=repo.get_user(payment.member_id)
    if not member: raise HTTPException(404,"Member not found")
    if callback_amount is not None:
        try:
            if float(callback_amount)!=float(payment.amount): payment.status=PaymentStatus.FAILED;repo.update_payment(payment);return {"message":"Payment amount mismatch"}
        except (TypeError,ValueError):
            payment.status=PaymentStatus.FAILED;repo.update_payment(payment);return {"message":"Invalid payment amount"}
    if callback_phone is not None:
        expected_phone=str(payment.phone).replace("+","")
        received_phone=str(callback_phone).replace("+","")
        if len(expected_phone)>=9 and len(received_phone)>=9 and expected_phone[-9:]!=received_phone[-9:]:
            payment.status=PaymentStatus.FAILED;repo.update_payment(payment);return {"message":"Payment phone mismatch"}
    payment.status=PaymentStatus.PAID
    payment.mpesa_receipt=receipt
    payment.paid_at=datetime.utcnow()
    if not member.membership_number: member.membership_number=generate_member_number()
    repo.update_payment(payment)
    repo.update_user(member)
    sms_message=f"JABALI registration successful. Welcome {member.first_name}. Member number: {member.membership_number}. Registration fee paid: KES {payment.amount}."
    try: sms_sent=send_sms(phone=member.phone,message=sms_message)
    except Exception: sms_sent=False
    return {"message":"Payment successful","member_id":str(member.user_id),"member_number":member.membership_number,"mpesa_receipt":receipt,"amount":payment.amount,"transaction_date":transaction_date,"sms":"sent" if sms_sent else "failed"}

def update_user(db:Session,user_id:uuid.UUID,data):
    repo=UserRepository(db)
    user=repo.get_user(user_id)
    if not user: raise HTTPException(404,"User not found")
    for field,value in data.model_dump(exclude_unset=True).items(): setattr(user,field,value)
    return repo.update_user(user)

def delete_user(db:Session,user_id:uuid.UUID):
    repo=UserRepository(db)
    user=repo.get_user(user_id)
    if not user: raise HTTPException(404,"User not found")
    repo.delete_user(user)
    return {"message":"User deleted successfully"}

def update_community_forest_association(db:Session,community_forest_association_id:uuid.UUID,data,current_user):
    repo=UserRepository(db)
    community_forest_association=repo.get_community_forest_association(community_forest_association_id)
    if not community_forest_association: raise HTTPException(404,"Community Forest Association not found")
    if community_forest_association.kenya_forest_service_official_id!=uuid.UUID(current_user["sub"]): raise HTTPException(403,"You do not manage this Community Forest Association")
    for field,value in data.model_dump(exclude_unset=True).items(): setattr(community_forest_association,field,value)
    return repo.update_community_forest_association(community_forest_association)

def delete_community_forest_association(db:Session,community_forest_association_id:uuid.UUID,current_user):
    repo=UserRepository(db)
    community_forest_association=repo.get_community_forest_association(community_forest_association_id)
    if not community_forest_association: raise HTTPException(404,"Community Forest Association not found")
    if community_forest_association.kenya_forest_service_official_id!=uuid.UUID(current_user["sub"]): raise HTTPException(403,"You do not manage this Community Forest Association")
    repo.delete_community_forest_association(community_forest_association)
    return {"message":"Community Forest Association deleted successfully"}