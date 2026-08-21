from fastapi import HTTPException
from sqlalchemy.orm import Session

from rejesha_green.repositories.user_repository import UserRepository
from rejesha_green.security import verify_password, create_access_token, create_refresh_token


def login(db: Session, email: str, password: str):
    user = UserRepository(db).get_by_email(email)

    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "access_token": create_access_token(str(user.user_id), user.role.value),
        "refresh_token": create_refresh_token(str(user.user_id)),
        "token_type": "bearer",
    }