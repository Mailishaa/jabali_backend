import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from rejesha_green.models.user import User, UserRole
from rejesha_green.repositories.permit_repository import (
    permit_repository,
)
from rejesha_green.schemas.permits import (
    PermitCreate,
    PermitInternalUpdate,
    PermitUpdate,
)

logger = logging.getLogger(__name__)


class PermitService:

    def get_member(
        self,
        db: Session,
        member_id: UUID,
        phone_number: str,
    ) -> User:
        member = (
            db.query(User)
.filter(User.user_id == member_id)
.first()
        )

        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found.",
            )

        if member.phone!= phone_number:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Member ID and phone number do not match.",
            )

        if not member.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Member account is inactive.",
            )

        if member.role!= UserRole.MEMBER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only registered members can request permits.",
            )
        if member.community_forest_association_id is None:
        
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Member is not assigned to a CFA.",
            )

        return member

    def create_permit(
        self,
        db: Session,
        data: PermitCreate,
    ):
        member = self.get_member(
            db=db,
            member_id=data.member_id,
            phone_number=data.phone_number,
        )

        existing = permit_repository.get_by_ussd_session_id(
            db,
            data.ussd_session_id,
        )

        if existing:
            return existing

        permit_data = {
            "member_id": member.user_id,
            "requested_resources": data.requested_resources,
            "phone_number": data.phone_number,
            "ussd_session_id": data.ussd_session_id,
            "current_step": "resource_selected",
            "permit_status": "ussd_started",
            "payment_status": "not_initiated",
            "is_available": True,
        }

        return permit_repository.create(
            db,
            permit_data,
        )

    def list_permits(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ):
        return permit_repository.get_all(
            db,
            skip,
            min(limit, 100),
        )

    def get_permit(
        self,
        db: Session,
        permit_id: int,
    ):
        permit = permit_repository.get(
            db,
            permit_id,
        )

        if not permit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permit not found.",
            )

        return permit

    def list_permits_for_member(
        self,
        db: Session,
        member_id: UUID,
    ):
        return permit_repository.get_by_member(
            db,
            member_id,
        )

    def update_permit(
        self,
        db: Session,
        permit_id: int,
        data: PermitUpdate,
    ):
        permit = self.get_permit(db, permit_id)

        if permit.payment_status in {
            "pending",
            "paid",
            "completed",
        }:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This permit cannot be edited.",
            )

        return permit_repository.update(
            db,
            permit,
            data,
        )

    def approve_permit(
        self,
        db: Session,
        permit_id: int,
    ):
        permit = self.get_permit(db, permit_id)

        if permit.payment_status not in {
            "paid",
            "completed",
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permit cannot be approved before payment.",
            )

        if permit.permit_status == "approved":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Permit is already approved.",
            )

        permit_number = (
            permit.permit_number
            or f"MAU-{datetime.now(timezone.utc):%Y%m%d}"
            f"-{permit.permit_id:06d}"
        )

        return permit_repository.update(
            db,
            permit,
            PermitInternalUpdate(
                permit_status="approved",
                permit_number=permit_number,
                issued_at=datetime.now(timezone.utc),
            ),
        )

    def delete_permit(
        self,
        db: Session,
        permit_id: int,
    ):
        permit = self.get_permit(db, permit_id)

        if permit.payment_status in {
            "paid",
            "completed",
        }:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A paid permit cannot be deleted.",
            )

        permit_repository.delete(db, permit)

    def list_pending_payments(self, db: Session):
        return permit_repository.get_pending_payments(db)

    def handle_ussd_request(
        self,
        db: Session,
        session_id: str,
        phone_number: str,
        text: str,
    ) -> str:
        member = (
            db.query(User)
.filter(User.phone == phone_number)
.first()
        )

        if not member:
            return (
                "END You must register as a member "
                "before requesting a permit."
            )

        if not member.is_active:
            return "END Your membership is inactive."

        if member.role!= UserRole.MEMBER:
            return "END Only registered members can request permits."

        if member.cfa_id is None:
            return "END You are not assigned to a CFA."

        parts = text.split("*") if text else []

        if not parts:
            return (
                "CON Welcome to Mau Forest\n"
                "1. Request permit\n"
                "2. Check permit status\n"
                "3. Exit"
            )

        if parts[0] == "1" and len(parts) == 1:
            return (
                "CON Select resource\n"
                "1. Firewood\n"
                "2. Bamboo\n"
                "3. Grass"
            )

        if parts[0] == "1" and len(parts) == 2:
            resources = {
                "1": "Firewood",
                "2": "Bamboo",
                "3": "Grass",
            }

            resource = resources.get(parts[1])

            if not resource:
                return "END Invalid resource selection."

            permit = self.create_permit(
                db,
                PermitCreate(
                    member_id=member.user_id,
                    phone_number=phone_number,
                    requested_resources=resource,
                    ussd_session_id=session_id,
                ),
            )

            return (
                "END Permit request received. "
                f"Your permit ID is {permit.permit_id}."
            )

        if parts[0] == "2":
            permits = permit_repository.get_by_member(
                db,
                member.user_id,
            )

            if not permits:
                return "END You have no permit requests."

            latest = permits[0]

            return (
                "END Permit status: "
                f"{latest.permit_status}. "
                f"Payment status: {latest.payment_status}."
            )

        if parts[0] == "3":
            return "END Thank you."

        return "END Invalid selection."


permit_service = PermitService()
