from fastapi import FastAPI

from database import Base, engine

from models.user import User, CFA, RegistrationPayment
from models.incident import IncidentReport
from models.permit import Permit
from models.forest_zone import ForestZone
from models.reforestation_log import TreeSurvivalLog
from models.activity import Activity


app = FastAPI(
    title="REJESHA API",
    version="1.0.0"
)


Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "application": "JABALI",
        "status": "running"
    }