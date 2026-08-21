from uuid import UUID

from sqlalchemy.orm import Session

from rejesha_green.models.activity import Activity
from rejesha_green.repositories.activity_repository import ActivityRepository
from rejesha_green.schemas.activities import (
    ActivityCreate,
    ActivityUpdate,
)
from rejesha_green.services.sms_service import SMSService


class ActivityService:

    def __init__(self, db: Session):
        self.repository = ActivityRepository(db)
        self.sms_service = SMSService()

    def create_activity(
        self,
        activity_data: ActivityCreate,
    ) -> Activity:

        activity = Activity(
            created_by=activity_data.created_by,
            zone_id=activity_data.zone_id,
            activity_name=activity_data.activity_name,
            scheduled_date=activity_data.scheduled_date,
            description=activity_data.description,
            user_group=activity_data.user_group,
            expected_attendees=activity_data.expected_attendees,
            actual_attendees=activity_data.actual_attendees,
        )

        # Save the activity to the database
        created_activity = self.repository.create(activity)

        # Build the SMS message
        message = (
            f"REJESHA GREEN: You have been notified of a new community activity.\n"
            f"Activity: {created_activity.activity_name}\n"
            f"Date: {created_activity.scheduled_date}\n"
            f"Group: {created_activity.user_group.value if created_activity.user_group else 'All Members'}\n"
            f"Expected participants: {created_activity.expected_attendees}\n"
            f"Location/Zone: {created_activity.zone_id}\n"
            f"Description: {created_activity.description or 'No additional details provided.'}\n"
            f"Please prepare to participate. Thank you."
        )

        return created_activity

    def get_activity(
        self,
        activity_id: str,
    ):
        return self.repository.get_by_id(activity_id)

    def get_activities(
        self,
        skip: int = 0,
        limit: int = 100,
    ):
        return self.repository.get_all(
            skip=skip,
            limit=limit,
        )

    def get_activities_by_zone(
        self,
        zone_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ):
        return self.repository.get_by_zone(
            zone_id=zone_id,
            skip=skip,
            limit=limit,
        )

    def get_upcoming_activities(
        self,
        skip: int = 0,
        limit: int = 100,
    ):
        return self.repository.get_upcoming(
            skip=skip,
            limit=limit,
        )

    def update_activity(
        self,
        activity_id: str,
        activity_data: ActivityUpdate,
    ):
        activity = self.repository.get_by_id(activity_id)

        if activity is None:
            return None

        update_data = activity_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(activity, field, value)

        return self.repository.update(activity)

    def delete_activity(
        self,
        activity_id: str,
    ):
        activity = self.repository.get_by_id(activity_id)

        if activity is None:
            return None

        self.repository.delete(activity)

        return activity