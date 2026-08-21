from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CommunityForestAssociationCreate(BaseModel):
    community_forest_association_name: str
    registration_fee: Decimal


class CommunityForestAssociationUpdate(BaseModel):
    community_forest_association_name: str | None = None
    registration_fee: Decimal | None = None
    is_active: bool | None = None


class CommunityForestAssociationResponse(BaseModel):
    community_forest_association_id: UUID
    community_forest_association_name: str
    kenya_forest_service_official_id: UUID
    registration_fee: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)