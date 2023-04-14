from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Boolean
from sqlalchemy import BIGINT
from sqlalchemy import Time
from sqlalchemy import SmallInteger
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from app.kernel.database import Base

class InnerPhone(Base):
    __tablename__ = "inner_phones"
    id = Column(BIGINT, primary_key=True)
    uuid = Column(String, unique=True)
    user_id = Column(BIGINT, ForeignKey('users.id', onupdate="CASCADE", ondelete="CASCADE"))
    phone_number = Column(BIGINT, unique=True)
    description = Column(Text, nullable=True)
    is_registration = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)
    duration_call = Column(Time, nullable=True)
    duration_conversation = Column(Time, nullable=True)
    incoming_calls = Column(SmallInteger, default=1)
    comment = Column(Text, nullable=True)
    users = relationship('UserModel',back_populates="inner_phone")