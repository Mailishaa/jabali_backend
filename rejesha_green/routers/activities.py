from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db

from rejesha_green.schemas.activities import (
    ActivityCreate,
    ActivityResponse,
    ActivityUpdate,
)
from rejesha_green.services.activity_service import ActivityService


router = APIRouter(
    prefix="/activities",
    tags=["Activities"],
)


@router.post(
    "/",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_activity(
    activity_data: ActivityCreate,
    db: Session = Depends(get_db),
):
    service = ActivityService(db)

    return service.create_activity(activity_data)


@router.get(
    "/",
    response_model=list[ActivityResponse],
)
def get_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = ActivityService(db)

    return service.get_activities(
        skip=skip,
        limit=limit,
    )


@router.get(
    "/upcoming",
    response_model=list[ActivityResponse],
)
def get_upcoming_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = ActivityService(db)

    return service.get_upcoming_activities(
        skip=skip,
        limit=limit,
    )


@router.get(
    "/zone/{zone_id}",
    response_model=list[ActivityResponse],
)
def get_activities_by_zone(
    zone_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = ActivityService(db)

    return service.get_activities_by_zone(
        zone_id=zone_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{activity_id}",
    response_model=ActivityResponse,
)
def get_activity(
    activity_id: str,
    db: Session = Depends(get_db),
):
    service = ActivityService(db)

    activity = service.get_activity(activity_id)

    if activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )

    return activity


@router.put(
    "/{activity_id}",
    response_model=ActivityResponse,
)
def update_activity(
    activity_id: str,
    activity_data: ActivityUpdate,
    db: Session = Depends(get_db),
):
    service = ActivityService(db)

    activity = service.update_activity(
        activity_id,
        activity_data,
    )

    if activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )

    return activity


@router.delete(
    "/{activity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_activity(
    activity_id: str,
    db: Session = Depends(get_db),
):
    service = ActivityService(db)

    activity = service.delete_activity(activity_id)

    if activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )

    return None