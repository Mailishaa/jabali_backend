from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from rejesha_green.config import settings
from rejesha_green.models.user import User, UserRole
from rejesha_green.models.community_forest_association import CommunityForestAssociation
from rejesha_green.models.registration_payment import RegistrationPayment
from rejesha_green.routers.auth import router as auth_router
from rejesha_green.routers.users import router as users_router
from rejesha_green.routers.community_forest_associations import router as cfa_router
from rejesha_green.routers.registration_payments import router as payment_router
from rejesha_green.security import hash_password


from rejesha_green.routers import forest_zone as forest_zone_routers

from rejesha_green.models.incident import IncidentReport
from rejesha_green.models.permit import Permit
from rejesha_green.models.reforestation_log import TreeSurvivalLog
from rejesha_green.routers import permits

from database import Base, engine
from rejesha_green.models.activity import Activity
from rejesha_green.models.forest_zone import ForestZone

from rejesha_green.routers.activities import router as activities_router


def onboard_default_admin():
    db: Session = SessionLocal()

    try:
        admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()

        if admin:
            return




        admin = User(
            national_id="SYSTEM-ADMIN",
            first_name=settings.ADMIN_FIRST_NAME,
            last_name=settings.ADMIN_LAST_NAME,
            phone=settings.ADMIN_PHONE,
            email=settings.ADMIN_EMAIL,
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            role=UserRole.SUPER_ADMIN,
            is_active=True,
        )

        db.add(admin)
        db.commit()

    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    onboard_default_admin()
    yield

from rejesha_green.routers import forest_zone as forest_zone_routers

from rejesha_green.models.incident import IncidentReport
from rejesha_green.models.permit import Permit
from rejesha_green.models.reforestation_log import TreeSurvivalLog
from rejesha_green.models.user import CFA, RegistrationPayment, User
from rejesha_green.routers import permits


app = FastAPI(
    title="REJESHA API",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(forest_zone_routers.router)



Base.metadata.create_all(bind=engine)
app.include_router(permits.router)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(cfa_router)
app.include_router(payment_router)



app.include_router(activities_router)


@app.get("/")

def root():
    return {
        "application": "JABALI",
        "status": "running",
    }