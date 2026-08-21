from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from rejesha_green.services.auth_service import login
from rejesha_green.schemas.users import UserLogin, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login_user(data: UserLogin, db: Session = Depends(get_db)):
    return login(db, data.email, data.password)