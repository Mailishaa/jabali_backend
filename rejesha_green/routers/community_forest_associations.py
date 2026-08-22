import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from rejesha_green.models.user import UserRole
from rejesha_green.repositories.community_forest_association_repository import CommunityForestAssociationRepository
from rejesha_green.schemas.community_forest_associations import CommunityForestAssociationCreate, CommunityForestAssociationResponse, CommunityForestAssociationUpdate
from rejesha_green.security import require_role
from rejesha_green.services import community_forest_association_service

router = APIRouter(prefix="/community-forest-associations", tags=["Community Forest Associations"])

@router.post("/", response_model=CommunityForestAssociationResponse, status_code=status.HTTP_201_CREATED)
def create_cfa(data: CommunityForestAssociationCreate, db: Session = Depends(get_db), current_user=Depends(require_role(UserRole.KENYA_FOREST_SERVICE_OFFICIAL))): 
    return community_forest_association_service.create_community_forest_association(db, data, current_user)

@router.get("/", response_model=list[CommunityForestAssociationResponse])
def get_cfas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user=Depends(require_role(UserRole.SUPER_ADMIN))): 
    return CommunityForestAssociationRepository(db).get_all(skip, limit)

@router.get("/{cfa_id}", response_model=CommunityForestAssociationResponse)
def get_cfa(cfa_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(require_role(UserRole.SUPER_ADMIN))):
    cfa = CommunityForestAssociationRepository(db).get(cfa_id)
    if not cfa: raise HTTPException(404, "Community Forest Association not found")
    return cfa

@router.patch("/{cfa_id}", response_model=CommunityForestAssociationResponse)
def update_cfa(cfa_id: uuid.UUID, data: CommunityForestAssociationUpdate, db: Session = Depends(get_db), current_user=Depends(require_role(UserRole.KENYA_FOREST_SERVICE_OFFICIAL))): 
    return community_forest_association_service.update_community_forest_association(db, cfa_id, data, current_user)

@router.delete("/{cfa_id}")
def delete_cfa(cfa_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(require_role(UserRole.KENYA_FOREST_SERVICE_OFFICIAL))): 
    return community_forest_association_service.delete_community_forest_association(db, cfa_id, current_user)