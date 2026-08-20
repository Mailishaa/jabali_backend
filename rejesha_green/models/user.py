import enum,uuid
from datetime import datetime
from sqlalchemy import Boolean,Column,DateTime,Enum,ForeignKey,Numeric,String
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class UserRole(str,enum.Enum):
    SUPER_ADMIN="super_admin"
    KENYA_FOREST_SERVICE_OFFICIAL="kenya_forest_service_official"
    COMMUNITY_FOREST_ASSOCIATION_OFFICIAL="community_forest_association_official"
    MEMBER="member"

class UserGroup(str,enum.Enum):
    BEEKEEPING="beekeeping"
    TREE_PLANTING="tree_planting"
    FIREWOOD_COLLECTION="firewood_collection"
    ECO_TOURISM="eco_tourism"

class PaymentStatus(str,enum.Enum):
    PENDING="pending"
    PAID="paid"
    FAILED="failed"

class CommunityForestAssociation(Base):
    __tablename__="community_forest_associations"
    community_forest_association_id=Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    community_forest_association_name=Column(String(150),unique=True,nullable=False)
    kenya_forest_service_official_id=Column(UUID(as_uuid=True),ForeignKey("users.user_id"),nullable=False,index=True)
    registration_fee=Column(Numeric(10,2),nullable=False)
    is_active=Column(Boolean,default=True,nullable=False)
    created_at=Column(DateTime,default=datetime.utcnow,nullable=False)
    updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

class User(Base):
    __tablename__="users"
    user_id=Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    national_id=Column(String(20),unique=True,nullable=False,index=True)
    first_name=Column(String(50),nullable=False)
    last_name=Column(String(50),nullable=False)
    phone=Column(String(20),unique=True,nullable=False,index=True)
    email=Column(String(255),unique=True,nullable=True)
    password_hash=Column(String(255),nullable=True)
    role=Column(Enum(UserRole,values_callable=lambda x:[e.value for e in x]),nullable=False,index=True)   
    membership_number=Column(String(50),unique=True,nullable=True,index=True)
    user_group=Column(Enum(UserGroup,values_callable=lambda x:[e.value for e in x]),nullable=True)
    registered_by=Column(UUID(as_uuid=True),ForeignKey("users.user_id"),nullable=True,index=True)
    community_forest_association_id=Column(UUID(as_uuid=True),ForeignKey("community_forest_associations.community_forest_association_id"),nullable=True,index=True)
    block_name=Column(String(100),nullable=True)
    is_active=Column(Boolean,default=True,nullable=False)
    created_at=Column(DateTime,default=datetime.utcnow,nullable=False)
    updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)

class RegistrationPayment(Base):
    __tablename__="registration_payments"
    payment_id=Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    member_id=Column(UUID(as_uuid=True),ForeignKey("users.user_id"),nullable=False,index=True)
    community_forest_association_id=Column(UUID(as_uuid=True),ForeignKey("community_forest_associations.community_forest_association_id"),nullable=False,index=True)
    amount=Column(Numeric(10,2),nullable=False)
    phone=Column(String(20),nullable=False)
    checkout_request_id=Column(String(100),unique=True,nullable=True,index=True)
    merchant_request_id=Column(String(100),nullable=True)
    mpesa_receipt=Column(String(100),nullable=True)
    status=Column(Enum(PaymentStatus,values_callable=lambda x:[e.value for e in x]),default=PaymentStatus.PENDING,nullable=False)
    created_at=Column(DateTime,default=datetime.utcnow,nullable=False)
    paid_at=Column(DateTime,nullable=True)