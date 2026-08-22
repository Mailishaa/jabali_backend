from sqlalchemy.orm import Session

from rejesha_green.models.reforestation_log import TreeSurvivalLog


class TreeSurvivalRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, log_data):
        db_obj = TreeSurvivalLog(
        activity_id=log_data.activity_id,
        trees_planted=log_data.trees_planted,
        trees_surviving=log_data.trees_surviving,
        dead_trees=log_data.trees_planted - log_data.trees_surviving
    )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_all(self):
        return self.db.query(TreeSurvivalLog).all()

    def get(self, log_id):
        return self.db.query(TreeSurvivalLog).filter(
            TreeSurvivalLog.log_id == log_id
        ).first()

    def update(self, log_id, log_data):
        db_obj = self.get(log_id)

        if not db_obj:
            return None

        for key, value in log_data.model_dump().items():
            setattr(db_obj, key, value)

        self.db.commit()
        self.db.refresh(db_obj)

        return db_obj

    def delete(self, log_id):

        db_obj = self.get(log_id)

        if not db_obj:
            return None

        self.db.delete(db_obj)
        self.db.commit()

        return db_obj