from datetime import datetime
from decimal import Decimal
from uuid import UUID


from pydantic import BaseModel, ConfigDict, EmailStr


from rejesha_green.models.user import UserRole, UserGroup, PaymentStatus




class UserBase(BaseModel):
   national_id: str
   first_name: str
   last_name: str
   phone: str
   email: EmailStr | None = None
   user_group: UserGroup | None = None
   block_name: str | None = None




class UserCreate(UserBase):
   password: str | None = None
   role: UserRole
   cfa_id: UUID | None = None




class UserUpdate(BaseModel):
   first_name: str | None = None
   last_name: str | None = None
   phone: str | None = None
   email: EmailStr | None = None
   user_group: UserGroup | None = None
   block_name: str | None = None
   is_active: bool | None = None




class UserResponse(UserBase):
   user_id: UUID
   role: UserRole
   membership_number: str | None = None
   registered_by: UUID | None = None
   cfa_id: UUID | None = None
   is_active: bool
   created_at: datetime


   model_config = ConfigDict(from_attributes=True)




class CFAOfficialCreate(UserBase):
   password: str




class CFAOfficialResponse(UserResponse):
   pass




class CFACreate(BaseModel):
   cfa_name: str
   registration_fee: Decimal




class CFAOfficialAndCFACreate(BaseModel):
   cfa_name: str
   registration_fee: Decimal
   national_id: str
   first_name: str
   last_name: str
   phone: str
   email: EmailStr | None = None
   password: str




class CFAUpdate(BaseModel):
   cfa_name: str | None = None
   registration_fee: Decimal | None = None
   is_active: bool | None = None




class CFAResponse(BaseModel):
   cfa_id: UUID
   cfa_name: str
   kfs_official_id: UUID
   registration_fee: Decimal
   is_active: bool
   created_at: datetime


   model_config = ConfigDict(from_attributes=True)




class RegistrationPaymentResponse(BaseModel):
   payment_id: UUID
   member_id: UUID
   cfa_id: UUID
   amount: Decimal
   phone: str
   status: PaymentStatus
   checkout_request_id: str | None = None
   mpesa_receipt: str | None = None
   created_at: datetime


   model_config = ConfigDict(from_attributes=True)




class UserLogin(BaseModel):
   email: EmailStr
   password: str




LoginRequest = UserLogin




class TokenResponse(BaseModel):
   access_token: str
   refresh_token: str
   token_type: str = "bearer"
