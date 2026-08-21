import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from rejesha_green.models.user import UserRole
from rejesha_green.security import require_role
from rejesha_green.services import registration_payment_service

router = APIRouter(prefix="/registration-payments", tags=["Registration Payments"])

@router.post("/member/{member_id}")
def initiate_registration_payment(member_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(require_role(UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL))): 
    return registration_payment_service.initiate_registration_payment(db, member_id, current_user)

@router.post("/callback")
def registration_payment_callback(payload: dict, db: Session = Depends(get_db)): 
    return registration_payment_service.process_registration_payment(db, payload)