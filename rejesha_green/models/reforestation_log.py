import uuid
from datetime import datetime
from sqlalchemy import Column , Integer,DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import func



class TreeSurvivalLog(Base):
    __tablename__ = "tree_survival_logs"
    
    log_id = Column(UUID(as_uuid =True),primary_key=True,default=uuid.uuid4,index=True)
    activity_id = Column(UUID(as_uuid=True),nullable =False)
    trees_planted= Column(Integer,nullable=False)
    trees_surviving= Column(Integer,nullable=False)
    dead_trees=Column(Integer,nullable=False)
    updated_at= Column(DateTime,server_default=func.now(),nullable=False)