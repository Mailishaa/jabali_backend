from fastapi import FastAPI

from database import Base, engine
from rejesha_green.models.activity import Activity
from rejesha_green.models.forest_zone import ForestZone
from rejesha_green.models.incident import IncidentReport
from rejesha_green.models.permit import Permit
from rejesha_green.models.reforestation_log import TreeSurvivalLog
from rejesha_green.models.user import CFA, RegistrationPayment, User
from rejesha_green.routers import permits

app = FastAPI(
    title="REJESHA API",
    version="1.0.0"
)


Base.metadata.create_all(bind=engine)
app.include_router(permits.router)


@app.get("/")
def root():
    return {
        "application": "JABALI",
        "status": "running"
    }