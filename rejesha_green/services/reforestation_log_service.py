import uuid 
from typing import List
from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from rejesha_green.repositories.reforestation_log_repository import TreeSurvivalRepository
from rejesha_green.schemas.reforestation_logs import TreeSurvivalCreate, TreeSurvivalUpdate
from rejesha_green.models.reforestation_log import TreeSurvivalLog


class TreeSurvivalService:
    def __init__(self,db:Session):
        self.repository = TreeSurvivalRepository(db)
        
    def record_log(self,log_data:TreeSurvivalCreate):
        try:
            dead_trees_count =log_data.trees_planted - log_data.trees_surviving
            return self.repository.create_log(log_data,dead_trees_count)
        except Exception as e :
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Failed to record survival log:{str(e)}")    
    def fetch_log_by_id(self,log_id: uuid.UUID):
        return self.repository.get_logs_by_activity()
    def modify_log(self,log_id:uuid.UUID,log_data:TreeSurvivalUpdate):
        db_log =self.fetch_log_by_id(log_id)
        update_dict=log_data.model_dump(exclude_unset=True)
        
        if"trees_planted"in update_dict or "trees_surviving" in update_dict:
            planted = update_dict.get("trees_planted",db_log.trees_planted)
            surviving = update_dict.get("trees_surviving",db_log.trees_surviving)
            if surviving > planted:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail= "Surviving trees cannot exceed planted trees during updates."
                    
                )    
            update_dict["dead_trees"] =planted-surviving
        return self.repository.update_log(db_log,update_dict)
    def remove_log(self,log_id:uuid.UUID):
        db_log =self.fetch_log_by_id(log_id)
        self.repository.delete_log(db_log)
                