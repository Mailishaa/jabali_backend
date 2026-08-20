import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from rejesha_green.models.user import UserRole
from rejesha_green.repositories.user_repository import UserRepository
from rejesha_green.schemas.users import (
    CommunityForestAssociationOfficialCreate,
    CommunityForestAssociationResponse,
    CommunityForestAssociationUpdate,
    KenyaForestServiceOfficialCreate,
    MemberCreate,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from rejesha_green.security import require_role
from rejesha_green.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(
    data: UserCreate,
    current_user=Depends(require_role(UserRole.SUPER_ADMIN.value)),
    db: Session = Depends(get_db),
):
    return user_service.create_user(db, data)


@router.get("/", response_model=list[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(require_role(UserRole.SUPER_ADMIN.value)),
    db: Session = Depends(get_db),
):
    return UserRepository(db).get_all_users(skip, limit)


@router.get(
    "/community-forest-associations",
    response_model=list[CommunityForestAssociationResponse],
)
def get_community_forest_associations(
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(
        require_role(
            UserRole.SUPER_ADMIN.value,
            UserRole.KENYA_FOREST_SERVICE_OFFICIAL.value,
            UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL.value,
        )
    ),
    db: Session = Depends(get_db),
):
    return UserRepository(db).get_all_community_forest_associations(skip, limit)


@router.get(
    "/community-forest-associations/{community_forest_association_id}",
    response_model=CommunityForestAssociationResponse,
)
def get_community_forest_association(
    community_forest_association_id: uuid.UUID,
    current_user=Depends(
        require_role(
            UserRole.SUPER_ADMIN.value,
            UserRole.KENYA_FOREST_SERVICE_OFFICIAL.value,
            UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL.value,
        )
    ),
    db: Session = Depends(get_db),
):
    user = UserRepository(db).get_community_forest_association(
        community_forest_association_id
    )
    if not user:
        raise HTTPException(404, "Community Forest Association not found")
    return user


@router.patch(
    "/community-forest-associations/{community_forest_association_id}",
    response_model=CommunityForestAssociationResponse,
)
def update_community_forest_association(
    community_forest_association_id: uuid.UUID,
    data: CommunityForestAssociationUpdate,
    current_user=Depends(
        require_role(UserRole.KENYA_FOREST_SERVICE_OFFICIAL.value)
    ),
    db: Session = Depends(get_db),
):
    return user_service.update_community_forest_association(
        db, community_forest_association_id, data, current_user
    )


@router.delete(
    "/community-forest-associations/{community_forest_association_id}"
)
def delete_community_forest_association(
    community_forest_association_id: uuid.UUID,
    current_user=Depends(
        require_role(UserRole.KENYA_FOREST_SERVICE_OFFICIAL.value)
    ),
    db: Session = Depends(get_db),
):
    return user_service.delete_community_forest_association(
        db, community_forest_association_id, current_user
    )


@router.post(
    "/kenya-forest-service-official",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_kenya_forest_service_official(
    data: KenyaForestServiceOfficialCreate,
    current_user=Depends(require_role(UserRole.SUPER_ADMIN.value)),
    db: Session = Depends(get_db),
):
    return user_service.register_kenya_forest_service_official(
        db, data, current_user
    )


@router.post(
    "/community-forest-association-official",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_community_forest_association_official(
    data: CommunityForestAssociationOfficialCreate,
    current_user=Depends(
        require_role(UserRole.KENYA_FOREST_SERVICE_OFFICIAL.value)
    ),
    db: Session = Depends(get_db),
):
    return user_service.register_community_forest_association_official(
        db, data, current_user
    )


@router.post(
    "/member", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register_member(
    data: MemberCreate,
    current_user=Depends(
        require_role(UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL.value)
    ),
    db: Session = Depends(get_db),
):
    return user_service.register_member(db, data, current_user)


@router.post("/member/{member_id}/registration-payment")
def initiate_registration_payment(
    member_id: uuid.UUID,
    current_user=Depends(
        require_role(UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL.value)
    ),
    db: Session = Depends(get_db),
):
    return user_service.initiate_registration_payment(db, member_id, current_user)


@router.post("/registration-payment/callback")
def registration_payment_callback(
    payload: dict, db: Session = Depends(get_db)
):
    return user_service.process_registration_payment(db, payload)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: uuid.UUID,
    current_user=Depends(
        require_role(
            UserRole.SUPER_ADMIN.value,
            UserRole.KENYA_FOREST_SERVICE_OFFICIAL.value,
            UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL.value,
        )
    ),
    db: Session = Depends(get_db),
):
    user = UserRepository(db).get_user(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    current_user=Depends(require_role(UserRole.SUPER_ADMIN.value)),
    db: Session = Depends(get_db),
):
    return user_service.update_user(db, user_id, data)


@router.delete("/{user_id}")
def delete_user(
    user_id: uuid.UUID,
    current_user=Depends(require_role(UserRole.SUPER_ADMIN.value)),
    db: Session = Depends(get_db),
):
    return user_service.delete_user(db, user_id)
