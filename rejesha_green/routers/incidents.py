import uuid
from sqlalchemy.orm import Session
from database import get_db
from fastapi import APIRouter, Depends, Form, HTTPException, status
from rejesha_green.schemas.incidents import IncidentReportCreate, IncidentReportRead, IncidentReportUpdate
from rejesha_green.services import incident_service

router = APIRouter(prefix="/incidents", tags=["Incidents Report"])

@router.get("/")
def list_incidents(db: Session = Depends(get_db)):
    return incident_service.list_incident_report(db)

@router.get("/{id}", response_model=IncidentReportRead)
def get_incident(id: uuid.UUID, db: Session = Depends(get_db)):
    return incident_service.get_incident_report(db, id)

@router.post("/", response_model=IncidentReportRead, status_code=status.HTTP_201_CREATED)
def create_incident(data: IncidentReportCreate, db: Session = Depends(get_db)):
    return incident_service.create_incident_report(db, data)

@router.put("/{id}", response_model=IncidentReportRead)
def update_incident(id: uuid.UUID, data: IncidentReportUpdate, db: Session = Depends(get_db)):
    return incident_service.update_incident_report(db, id, data)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(id: uuid.UUID, db: Session = Depends(get_db)):
    incident_service.delete_incident_report(db, id)
    return None

