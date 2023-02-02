from sqlalchemy import Column, String, Boolean, BIGINT, SMALLINT, Integer, TIMESTAMP, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.kernel.database import Base

class UserModel(Base):
    __tablename__ = "users"
    id = Column(BIGINT, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    password = Column(String)
    name = Column(String)
    last_name = Column(String)
    patronymic = Column(String,nullable=True)
    login = Column(String)
    is_operator = Column(Boolean, default = False)
    phone = Column(String(15), nullable=True)
    inner_phone = Column(Integer, nullable=True)
    is_active = Column(Boolean, default = True)
    photo_path = Column(String, nullable=True)
    department_id = Column(SMALLINT, ForeignKey('departments.id'))
    date_employment_at = Column(TIMESTAMP)
    date_dismissal_at = Column(TIMESTAMP, nullable=True) 
    created_at = Column(TIMESTAMP,server_default=func.now())
    updated_at = Column(TIMESTAMP,server_default=func.now(),onupdate=func.now()) 
    # Relationships
    deparment = relationship("DepartmentsModel")
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
               f"department_id ={self.department_id }"\
               f"date_employment_at={self.date_employment_at}"\
               f"date_dismissal_at={self.date_dismissal_at}"\
               f"created_at={self.created_at}"\
               f"updated_at={self.updated_at})>"


class DepartmentsModel(Base):
    
    __tablename__ = "departments"

    id = Column(SMALLINT, primary_key=True)
    name = Column(String(30))
    def __repr__(self) -> str:
        return f"<Departments(id={self.id}, " \
            f"name={self.name})>"