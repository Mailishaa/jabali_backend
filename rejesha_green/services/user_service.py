import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session
from rejesha_green.models.user import User, UserRole
from rejesha_green.repositories.user_repository import UserRepository
from rejesha_green.repositories.community_forest_association_repository import CommunityForestAssociationRepository
from rejesha_green.security import hash_password

def generate_member_number(): return f"JAB-{uuid.uuid4().hex[:8].upper()}"

def validate_user(repo, data, require_password=False):
    if repo.get_by_national_id(data.national_id): raise HTTPException(400, "National ID already exists")
    if repo.get_by_phone(data.phone): raise HTTPException(400, "Phone number already exists")
    if data.email and repo.get_by_email(data.email): raise HTTPException(400, "Email already exists")
    if require_password and not data.password: raise HTTPException(400, "Password is required")

def create_user_record(data, role, registered_by=None, cfa_id=None):
    return User(
        national_id=data.national_id, first_name=data.first_name, last_name=data.last_name,
        phone=data.phone, email=data.email if role != UserRole.MEMBER else None,
        password_hash=hash_password(data.password) if role != UserRole.MEMBER and data.password else None,
        role=role, user_group=data.user_group if role == UserRole.MEMBER else None,
        block_name=data.block_name if role == UserRole.MEMBER else None,
        registered_by=registered_by, community_forest_association_id=cfa_id
    )

def create_user(db: Session, data):
    repo = UserRepository(db)
    if not data.role: raise HTTPException(400, "User role is required")
    validate_user(repo, data, data.role != UserRole.MEMBER)
    return repo.create_user(create_user_record(data, data.role, cfa_id=data.community_forest_association_id))

def register_kenya_forest_service_official(db: Session, data, current_user):
    repo = UserRepository(db)
    validate_user(repo, data, True)
    user = create_user_record(data, UserRole.KENYA_FOREST_SERVICE_OFFICIAL, registered_by=uuid.UUID(current_user["sub"]))
    return repo.create_user(user)

def register_community_forest_association_official(db: Session, data, current_user):
    user_repo = UserRepository(db)
    cfa_repo = CommunityForestAssociationRepository(db)
    kfs_id = uuid.UUID(current_user["sub"])
    kfs = user_repo.get_user(kfs_id)
    if not kfs or kfs.role != UserRole.KENYA_FOREST_SERVICE_OFFICIAL: raise HTTPException(403, "Invalid Kenya Forest Service Official")
    cfa = cfa_repo.get(data.community_forest_association_id)
    if not cfa: raise HTTPException(404, "Community Forest Association not found")
    if cfa.kenya_forest_service_official_id != kfs_id: raise HTTPException(403, "You do not manage this Community Forest Association")
    validate_user(user_repo, data, True)
    user = create_user_record(data, UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL, registered_by=kfs_id, cfa_id=cfa.community_forest_association_id)
    return user_repo.create_user(user)

def register_member(db: Session, data, current_user):
    repo = UserRepository(db)
    official_id = uuid.UUID(current_user["sub"])
    official = repo.get_user(official_id)
    if not official or official.role != UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL: raise HTTPException(403, "Only a Community Forest Association Official can register members")
    validate_user(repo, data)
    user = create_user_record(data, UserRole.MEMBER, registered_by=official_id, cfa_id=official.community_forest_association_id)
    return repo.create_user(user)

def update_user(db: Session, user_id: uuid.UUID, data, current_user):
    repo = UserRepository(db)
    user = repo.get_user(user_id)
    if not user: raise HTTPException(404, "User not found")
    for field, value in data.model_dump(exclude_unset=True).items(): setattr(user, field, value)
    return repo.update_user(user)

def delete_user(db: Session, user_id: uuid.UUID):
    repo = UserRepository(db)
    user = repo.get_user(user_id)
    if not user: raise HTTPException(404, "User not found")
    user.is_active = False
    return repo.update_user(user)