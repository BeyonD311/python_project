from datetime import datetime
from sqlalchemy import Column, String, Boolean, BIGINT, SMALLINT, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.kernel.database import Base
from .departments import DepartmentsModel

class UserModel(Base):
    __tablename__ = "users"
    id = Column(BIGINT, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    password = Column(String)
    name = Column(String)
    last_name = Column(String)
    patronymic = Column(String, default=False)
    login = Column(String)
    is_operator = Column(Boolean, default=False)
    phone = Column(String(15), default=False)
    inner_phone = Column(Integer, default=False)
    is_active = Column(Boolean, default=True)
    photo_path = Column(String, default="")
    # department_id = Column(SMALLINT, ForeignKey('departments.id'))
    deparment = relationship("DepartmentsModel", back_populates="children")
    date_employment_at = Column(DateTime)
    date_dismissal_at = Column(DateTime, default=None)
    created_at = Column(DateTime,onupdate=datetime.now)
    updated_at = Column(DateTime,onupdate=datetime.now)
    def __repr__(self):
        return f"<User(id={self.id}, " \
               f"email=\"{self.email}\", " \
               f"hashed_password=\"{self.hashed_password}\", " \
               f"is_active={self.is_active}"\
               f"name={self.name}"\
               f"last_name={self.last_name}"\
               f"patronymic={self.patronymic}"\
               f"login={self.login}"\
               f"phone={self.phone}"\
               f"inner_phone={self.inner_phone}"\
               f"photo_path={self.photo_path}"\
               f"deparment={self.deparment}" \
               f"date_employment_at={self.date_employment_at}"\
               f"date_dismissal_at={self.date_dismissal_at}"\
               f"created_at={self.created_at}"\
               f"updated_at={self.updated_at})>"\


