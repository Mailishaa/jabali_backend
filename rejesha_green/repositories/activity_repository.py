from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from rejesha_green.models.activity import Activity, ActivityStatus


class ActivityRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, activity: Activity) -> Activity:
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)

        return activity

    def get_by_id(self, activity_id: str):
        return (
            self.db.query(Activity)
            .filter(Activity.activity_id == activity_id)
            .first()
        )

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ):
        return (
            self.db.query(Activity)
            .order_by(Activity.scheduled_date.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_zone(
        self,
        zone_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ):
        return (
            self.db.query(Activity)
            .filter(Activity.zone_id == zone_id)
            .order_by(Activity.scheduled_date.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_upcoming(
        self,
        skip: int = 0,
        limit: int = 100,
    ):
        return (
            self.db.query(Activity)
            .filter(Activity.status == ActivityStatus.UPCOMING)
            .filter(Activity.scheduled_date >= datetime.utcnow())
            .order_by(Activity.scheduled_date.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, activity: Activity) -> Activity:
        self.db.commit()
        self.db.refresh(activity)

        return activity

    def delete(self, activity: Activity):
        self.db.delete(activity)
        self.db.commit()