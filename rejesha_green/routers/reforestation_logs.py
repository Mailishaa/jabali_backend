import uuid
from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from rejesha_green.schemas.reforestation_logs import (
    TreeSurvivalLogCreate,
    TreeSurvivalLogUpdate,
    TreeSurvivalLogRead
)
from rejesha_green.repositories.reforestation_log_repository import TreeSurvivalRepository


router = APIRouter(prefix="/tree-survival",tags=["Tree Survival Tracking"])
@router.post(
    "/",
    response_model=TreeSurvivalLogRead,
    status_code=status.HTTP_201_CREATED
)
def create_survival_log(
    log_data: TreeSurvivalLogCreate,
    db: Session = Depends(get_db)
):
    repo = TreeSurvivalRepository(db)
    new_log = repo.create(log_data)
    return new_log


@router.get("/", response_model=List[TreeSurvivalLogRead])
def get_all_survival_logs(db: Session = Depends(get_db)):
    repo = TreeSurvivalRepository(db)
    return repo.get_all()

@router.get("/{log_id}",response_model=TreeSurvivalLogRead)
def get_survival_log(log_id: uuid.UUID,db: Session = Depends(get_db)):
    repo = TreeSurvivalRepository(db)
    log = repo.get(log_id)
    if not log:raise HTTPException(
            status_code=404,
            detail="Tree survival log not found")
    return log

@router.put("/{log_id}",response_model=TreeSurvivalLogRead)
def update_survival_log(log_id: uuid.UUID,log_data: TreeSurvivalLogUpdate,db: Session = Depends(get_db)):
    repo = TreeSurvivalRepository(db)
    updated_log = repo.update(log_id, log_data)
    if not updated_log:
        raise HTTPException(
            status_code=404,
            detail="Tree survival log cannot be found"
        )
    return updated_log


@router.delete("/{log_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_survival_log(log_id: uuid.UUID,db: Session = Depends(get_db)):
    repo = TreeSurvivalRepository(db)
    deleted_log = repo.delete(log_id)
    if not deleted_log:raise HTTPException(
            status_code=404,
            detail="Tree survival log cannot be found")

    return None