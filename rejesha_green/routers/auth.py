from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


from database import get_db
from rejesha_green.repositories.user_repository import UserRepository
from rejesha_green.schemas.users import UserLogin, TokenResponse
from rejesha_green.security import (
   verify_password,
   create_access_token,
   create_refresh_token,
)




router = APIRouter(
   prefix="/auth",
   tags=["Authentication"],
)




@router.post("/login", response_model=TokenResponse)
def login(
   data: UserLogin,
   db: Session = Depends(get_db),
):
   repo = UserRepository(db)
   user = repo.get_by_email(data.email)


   if not user or not user.password_hash:
       raise HTTPException(
           status_code=401,
           detail="Invalid email or password",
       )


   if not user.is_active:
       raise HTTPException(
           status_code=403,
           detail="User account is inactive",
       )


   if not verify_password(
       data.password,
       user.password_hash,
   ):
       raise HTTPException(
           status_code=401,
           detail="Invalid email or password",
       )


   return {
       "access_token": create_access_token(
           str(user.user_id),
           user.role.value,
       ),
       "refresh_token": create_refresh_token(
           str(user.user_id),
       ),
       "token_type": "bearer",
   }
