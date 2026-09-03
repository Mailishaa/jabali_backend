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
from fastapi.responses import PlainTextResponse

from rejesha_green.services.permit_service import handle_ussd


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

    now = time.time()

    timestamps = ussd_rate_limit_store.setdefault(
        phoneNumber,
        []
    )

    timestamps = [
        t for t in timestamps
        if t > now - LIMIT_WINDOW_SECONDS
    ]

    if len(timestamps) >= MAX_REQUESTS_PER_WINDOW:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Try again later."
        )

    timestamps.append(now)

    ussd_rate_limit_store[phoneNumber] = timestamps

    return phoneNumber



@router.post(
    "",
    response_class=PlainTextResponse,
)
async def handle_ussd_request(
    sessionId: str = Form(...),
    serviceCode: str = Form(...),
    text: str = Form(""),
    phoneNumber: str = Depends(check_ussd_rate_limit),
    db: Session = Depends(get_db),
):
    # CHANGED:
    # All USSD navigation is now handled by one service.
    return handle_ussd(
        db=db,
        session_id=sessionId,
        phone_number=phoneNumber,
        text=text,
    )