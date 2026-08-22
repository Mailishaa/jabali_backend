import uuid
from datetime import datetime
from pydantic import BaseModel,Field,model_validator ,ConfigDict
from typing import Optional

class TreeSurvivalLogBase(BaseModel):
    activity_id: uuid.UUID
    trees_planted: int = Field(..., ge=0, description="Total trees planted")
    trees_surviving: int = Field(..., ge=0, description="Total trees surviving")
    @model_validator(mode="after")
    def validate_tree_counts(self):
            if self.trees_surviving > self.trees_planted:
             raise ValueError("Surviving trees cannot exceed planted trees")
            return self


    
class TreeSurvivalLogCreate(TreeSurvivalLogBase):
        pass
    
class TreeSurvivalLogUpdate(BaseModel):
        activity_id:Optional [uuid.UUID] =None
        dead_trees:Optional[int] = None
        
        
class TreeSurvivalLogRead(TreeSurvivalLogBase):
        model_config = ConfigDict(from_attributes=True)
        log_id: uuid.UUID
        dead_trees:int