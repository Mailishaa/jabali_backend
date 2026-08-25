import uuid

from sqlalchemy.orm import Session

from rejesha_green.models.incident import IncidentReport


class IncidentReportRepository:

    def __init__(self):
        self.model = IncidentReport

    def get(
        self,
        db: Session,
        incident_id: uuid.UUID
    ):
        return (
            db.query(self.model)
            .filter(self.model.incident_id == incident_id)
            .first()
        )

    def get_all(self, db: Session):
        return db.query(self.model).all()

    def create_incident_report(
        self,
        db: Session,
        data: dict
    ):
        incident = self.model(**data)

        db.add(incident)
        db.commit()
        db.refresh(incident)

        return incident

    def update(
        self,
        db: Session,
        db_obj: IncidentReport,
        data: dict
    ):
        for field, value in data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)

        return db_obj

    def delete(
        self,
        db: Session,
        db_obj: IncidentReport
    ):
        db.delete(db_obj)
        db.commit()

        return db_obj


incident_report_repository = IncidentReportRepository()