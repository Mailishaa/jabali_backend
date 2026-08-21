import time

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from database import get_db

from rejesha_green.services.ussd_service import handle_ussd


router = APIRouter(
    prefix="/ussd",
    tags=["USSD"]
)

ussd_rate_limit_store = {}

LIMIT_WINDOW_SECONDS = 60
MAX_REQUESTS_PER_WINDOW = 10


def check_ussd_rate_limit(
    phoneNumber: str = Form(...)
):
    current_time = time.time()

    if phoneNumber not in ussd_rate_limit_store:
        ussd_rate_limit_store[phoneNumber] = []

    timestamps = ussd_rate_limit_store[phoneNumber]

    valid_timestamps = [
        timestamp
        for timestamp in timestamps
        if timestamp > current_time - LIMIT_WINDOW_SECONDS
    ]

    if len(valid_timestamps) >= MAX_REQUESTS_PER_WINDOW:
        ussd_rate_limit_store[phoneNumber] = valid_timestamps

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )

    valid_timestamps.append(current_time)

    ussd_rate_limit_store[phoneNumber] = valid_timestamps

    return phoneNumber


@router.post("")
def handle_ussd_report(
    sessionId: str = Form(...),
    serviceCode: str = Form(...),
    text: str = Form(""),
    phoneNumber: str = Depends(check_ussd_rate_limit),
    db: Session = Depends(get_db),
):
    return handle_ussd(
        db=db,
        text=text
    )