from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Boolean
from sqlalchemy import BIGINT
from sqlalchemy import Float
from sqlalchemy import SmallInteger
from sqlalchemy import Time
from sqlalchemy.orm import relationship
from app.kernel.database import Base

class InnerPhone(Base):
    __tablename__ = "inner_phones"
    id = Column(BIGINT, primary_key=True)
    uuid = Column(String, unique=True)
    description = Column(Text, nullable=True)
    is_registration = Column(Boolean, default=False)
    login = Column(String, nullable=True)
    password = Column(String, nullable=True)
    duration_call = Column(Float, nullable=True)
    duration_conversation = Column(Float, nullable=True)
    incoming_calls = Column(SmallInteger, default=1)
    min_time = Column(Time, nullable=True)
    max_time = Column(Time, nullable=True)
    comment = Column(Text, nullable=True)
    users = relationship("UserModel", back_populates="inner_phone")