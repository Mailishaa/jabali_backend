from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from rejesha_green.models.user import User, UserRole
from rejesha_green.routers.users import router as users_router
from rejesha_green.routers.auth import router as auth_router
from rejesha_green.security import hash_password
from rejesha_green.config import settings

from rejesha_green.models.user import User



def onboard_default_admin():
    db: Session = SessionLocal()

    try:
        admin = (
            db.query(User)
            .filter(User.email == settings.ADMIN_EMAIL)
            .first()
        )

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


app = FastAPI(
    title="REJESHA API",
    version="1.0.0",
    lifespan=lifespan,
)


Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(users_router)


@app.get("/")
def root():
    return {
        "application": "JABALI",
        "status": "running",
    }