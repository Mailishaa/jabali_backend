from database import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import relationship


class Permit(Base):
   __tablename__ = "permits"


   permit_id = Column(Integer, primary_key=True, index=True)
   member_id = Column(Integer, nullable=False) 
   requested_resources = Column(String(200), nullable=False)
   base_fee = Column(Numeric(10, 2), nullable=False)
   is_available = Column(Boolean, nullable=False, default=True)
   permit_number = Column(String(50), unique=True, index=True, nullable=False)
   status = Column(String(20), nullable=False, default="pending") 
   max_permit = Column(Integer, nullable=False)
   issued_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


   payments = relationship("Payment", back_populates="permit")