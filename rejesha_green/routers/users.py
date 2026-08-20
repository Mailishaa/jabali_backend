import uuid


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from database import get_db
from rejesha_green.schemas.users import (
   UserCreate,
   UserUpdate,
   UserResponse,
   CFAUpdate,
   CFAResponse,
   CFAOfficialAndCFACreate,
)
from rejesha_green.repositories.user_repository import UserRepository
from rejesha_green.security import require_role
from rejesha_green.services import user_service




router = APIRouter(
   prefix="/users",
   tags=["Users"],
)




@router.post(
   "/",
   response_model=UserResponse,
   status_code=status.HTTP_201_CREATED,
)
def create_user(
   data: UserCreate,
   current_user=Depends(require_role("super_admin")),
   db: Session = Depends(get_db),
):
   return user_service.create_user(db, data)




@router.get(
   "/",
   response_model=list[UserResponse],
)
def get_users(
   skip: int = 0,
   limit: int = 100,
   current_user=Depends(require_role("super_admin")),
   db: Session = Depends(get_db),
):
   return UserRepository(db).get_all_users(skip, limit)




@router.get(
   "/{user_id}",
   response_model=UserResponse,
)
def get_user(
   user_id: uuid.UUID,
   current_user=Depends(require_role(
       "super_admin",
       "kfs_official",
       "cfa_official",
       "member",
   )),
   db: Session = Depends(get_db),
):
   user = UserRepository(db).get_user(user_id)


   if not user:
       raise HTTPException(404, "User not found")


   return user




@router.patch(
   "/{user_id}",
   response_model=UserResponse,
)
def update_user(
   user_id: uuid.UUID,
   data: UserUpdate,
   current_user=Depends(require_role("super_admin")),
   db: Session = Depends(get_db),
):
   return user_service.update_user(db, user_id, data)




@router.delete("/{user_id}")
def delete_user(
   user_id: uuid.UUID,
   current_user=Depends(require_role("super_admin")),
   db: Session = Depends(get_db),
):
   return user_service.delete_user(db, user_id)




@router.post(
   "/super-admin/kfs-official",
   response_model=UserResponse,
   status_code=status.HTTP_201_CREATED,
)
def register_kfs_official(
   data: UserCreate,
   current_user=Depends(require_role("super_admin")),
   db: Session = Depends(get_db),
):
   return user_service.register_kfs_official(
       db,
       data,
       current_user,
   )




@router.post(
   "/kfs/{kfs_id}/cfa-official",
   response_model=UserResponse,
   status_code=status.HTTP_201_CREATED,
)
def register_cfa_official(
   kfs_id: uuid.UUID,
   data: CFAOfficialAndCFACreate,
   current_user=Depends(require_role("kfs_official")),
   db: Session = Depends(get_db),
):
   return user_service.register_cfa_official(
       db,
       kfs_id,
       data,
       current_user,
   )




@router.post(
   "/cfa/{cfa_id}/member",
   response_model=UserResponse,
   status_code=status.HTTP_201_CREATED,
)
def register_member(
   cfa_id: uuid.UUID,
   data: UserCreate,
   current_user=Depends(require_role("cfa_official")),
   db: Session = Depends(get_db),
):
   return user_service.register_member(
       db,
       cfa_id,
       data,
       current_user,
   )






@router.post("/member/{member_id}/registration-payment")
def initiate_registration_payment(member_id: uuid.UUID, current_user=Depends(require_role("cfa_official")), db: Session = Depends(get_db)):
   return user_service.initiate_registration_payment(db, member_id, current_user)




@router.post(
   "/registration-payment/callback",
)
def registration_payment_callback(
   payload: dict,
   db: Session = Depends(get_db),
):
   return user_service.process_registration_payment(
       db,
       payload,
   )


@router.get(
   "/cfas",
   response_model=list[CFAResponse],
)
def get_cfas(
   skip: int = 0,
   limit: int = 100,
   current_user=Depends(require_role(
       "super_admin",
       "kfs_official",
       "cfa_official",
       "member",
   )),
   db: Session = Depends(get_db),
):
   return UserRepository(db).get_all_cfas(skip, limit)




@router.get(
   "/cfas/{cfa_id}",
   response_model=CFAResponse,
)
def get_cfa(
   cfa_id: uuid.UUID,
   current_user=Depends(require_role(
       "super_admin",
       "kfs_official",
       "cfa_official",
       "member",
   )),
   db: Session = Depends(get_db),
):
   cfa = UserRepository(db).get_cfa(cfa_id)


   if not cfa:
       raise HTTPException(404, "CFA not found")


   return cfa




@router.patch(
   "/cfas/{cfa_id}",
   response_model=CFAResponse,
)
def update_cfa(
   cfa_id: uuid.UUID,
   data: CFAUpdate,
   current_user=Depends(require_role("kfs_official")),
   db: Session = Depends(get_db),
):
   return user_service.update_cfa(
       db,
       cfa_id,
       data,
       current_user,
   )




@router.delete("/cfas/{cfa_id}")
def delete_cfa(
   cfa_id: uuid.UUID,
   current_user=Depends(require_role("kfs_official")),
   db: Session = Depends(get_db),
):
   return user_service.delete_cfa(
       db,
       cfa_id,
       current_user,
   )
