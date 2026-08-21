import uuid 
from datetime import datetime
from pydantic import  BaseModel,ConfigDict
from rejesha_green.models.incident import ActivityType
from typing import Optional


class IncidentReportBase(BaseModel):
    zone_id:uuid.UUID
    incident_type:ActivityType
    reported_at: Optional[datetime]=None 

class IncidentReportCreate(IncidentReportBase):
    pass

class IncidentReportUpdate(BaseModel):
    
    zone_id: Optional[uuid.UUID]  =None
    incident_type: Optional[ActivityType] =None
    
class IncidentReportRead(IncidentReportBase):
    model_config = ConfigDict(from_attributes=True)
    
    incident_id: uuid.UUID
    reported_at:datetime   
            
    