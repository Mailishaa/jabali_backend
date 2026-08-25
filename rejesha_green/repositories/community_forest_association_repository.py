from uuid import UUID
from sqlalchemy.orm import Session
from rejesha_green.models.community_forest_association import CommunityForestAssociation

class CommunityForestAssociationRepository:
    def __init__(self, db: Session): self.db = db
    def create(self, cfa: CommunityForestAssociation): self.db.add(cfa); self.db.commit(); self.db.refresh(cfa); return cfa
    def get(self, cfa_id: UUID): return self.db.query(CommunityForestAssociation).filter(CommunityForestAssociation.community_forest_association_id == cfa_id).first()
    def get_all(self, skip=0, limit=100): return self.db.query(CommunityForestAssociation).offset(skip).limit(limit).all()
    def get_by_name(self, name: str): return self.db.query(CommunityForestAssociation).filter(CommunityForestAssociation.community_forest_association_name == name).first()
    def update(self, cfa: CommunityForestAssociation): self.db.commit(); self.db.refresh(cfa); return cfa
    def delete(self, cfa: CommunityForestAssociation): self.db.delete(cfa); self.db.commit()

community_forest_association_repository = CommunityForestAssociationRepository