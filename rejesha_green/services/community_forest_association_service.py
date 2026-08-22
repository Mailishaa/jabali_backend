import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session
from rejesha_green.models.user import UserRole
from rejesha_green.models.community_forest_association import CommunityForestAssociation
from rejesha_green.repositories.user_repository import UserRepository
from rejesha_green.repositories.community_forest_association_repository import CommunityForestAssociationRepository

def create_community_forest_association(db: Session, data, current_user):
    user_repo = UserRepository(db)
    cfa_repo = CommunityForestAssociationRepository(db)
    kfs_id = uuid.UUID(current_user["sub"])
    kfs = user_repo.get_user(kfs_id)
    if not kfs or kfs.role != UserRole.KENYA_FOREST_SERVICE_OFFICIAL: raise HTTPException(403, "Only a Kenya Forest Service Official can create a Community Forest Association")
    if cfa_repo.get_by_name(data.community_forest_association_name): raise HTTPException(400, "Community Forest Association already exists")
    cfa = CommunityForestAssociation(community_forest_association_name=data.community_forest_association_name, kenya_forest_service_official_id=kfs_id, registration_fee=data.registration_fee)
    return cfa_repo.create(cfa)

def update_community_forest_association(db: Session, cfa_id: uuid.UUID, data, current_user):
    repo = CommunityForestAssociationRepository(db)
    cfa = repo.get(cfa_id)
    if not cfa: raise HTTPException(404, "Community Forest Association not found")
    if cfa.kenya_forest_service_official_id != uuid.UUID(current_user["sub"]): raise HTTPException(403, "You do not manage this Community Forest Association")
    for field, value in data.model_dump(exclude_unset=True).items(): setattr(cfa, field, value)
    return repo.update(cfa)

def delete_community_forest_association(db: Session, cfa_id: uuid.UUID, current_user):
    repo = CommunityForestAssociationRepository(db)
    cfa = repo.get(cfa_id)
    if not cfa: raise HTTPException(404, "Community Forest Association not found")
    if cfa.kenya_forest_service_official_id != uuid.UUID(current_user["sub"]): raise HTTPException(403, "You do not manage this Community Forest Association")
    cfa.is_active = False
    repo.update(cfa)
    return {"message": "Community Forest Association deactivated successfully"}