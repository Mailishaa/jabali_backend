from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel,ConfigDict,EmailStr
from rejesha_green.models.user import UserRole,UserGroup,PaymentStatus

class UserBase(BaseModel):
    national_id:str
    first_name:str
    last_name:str
    phone:str

class OfficialCreate(UserBase):
    email:EmailStr
    password:str

class KenyaForestServiceOfficialCreate(OfficialCreate):
    pass
class CommunityForestAssociationOfficialCreate(OfficialCreate):
    community_forest_association_name:str
    registration_fee:Decimal

class MemberCreate(UserBase):
    user_group:UserGroup|None=None
    block_name:str|None=None

class UserCreate(UserBase):
    email:EmailStr|None=None
    password:str|None=None
    role:UserRole|None=None
    user_group:UserGroup|None=None
    block_name:str|None=None
    community_forest_association_id:UUID|None=None

class UserUpdate(BaseModel):
    first_name:str|None=None
    last_name:str|None=None
    phone:str|None=None
    email:EmailStr|None=None
    user_group:UserGroup|None=None
    block_name:str|None=None
    is_active:bool|None=None

class UserResponse(BaseModel):
    user_id:UUID
    national_id:str
    first_name:str
    last_name:str
    phone:str
    email:EmailStr|None=None
    role:UserRole
    membership_number:str|None=None
    user_group:UserGroup|None=None
    registered_by:UUID|None=None
    community_forest_association_id:UUID|None=None
    block_name:str|None=None
    is_active:bool
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)

class CommunityForestAssociationCreate(BaseModel):
    community_forest_association_name:str
    registration_fee:Decimal

class CommunityForestAssociationUpdate(BaseModel):
    community_forest_association_name:str|None=None
    registration_fee:Decimal|None=None
    is_active:bool|None=None

class CommunityForestAssociationResponse(BaseModel):
    community_forest_association_id:UUID
    community_forest_association_name:str
    kenya_forest_service_official_id:UUID
    registration_fee:Decimal
    is_active:bool
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)

class RegistrationPaymentResponse(BaseModel):
    payment_id:UUID
    member_id:UUID
    community_forest_association_id:UUID
    amount:Decimal
    phone:str
    status:PaymentStatus
    checkout_request_id:str|None=None
    mpesa_receipt:str|None=None
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email:EmailStr
    password:str

LoginRequest=UserLogin

class TokenResponse(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str="bearer"