from sqlalchemy import Column, String, Boolean, BIGINT, SMALLINT, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.kernel.database import Base

class UserModel(Base):
    __tablename__ = "users"
    id = Column(BIGINT, primary_key=True, autoincrement='ignore_fk')
    email = Column(String, unique=True, nullable = False)
    hashed_password = Column(String)
    password = Column(String)
    name = Column(String, nullable=False) 
    last_name = Column(String, nullable=False)
    patronymic = Column(String,nullable=True)
    fio = Column(String)
    login = Column(String, unique=True, nullable = False)
    is_operator = Column(Boolean, default = False)
    phone = Column(String(25), nullable=True)
    inner_phone = Column(Integer, nullable=True)
    is_active = Column(Boolean, default = True) 
    photo_path = Column(String, nullable=True)
    position_id = Column(SMALLINT, ForeignKey('position.id'))
    status_id = Column(Integer, ForeignKey('status_users.id'))
    date_employment_at = Column(TIMESTAMP)
    date_dismissal_at = Column(TIMESTAMP, nullable=True) 
    created_at = Column(TIMESTAMP,server_default=func.now())
    updated_at = Column(TIMESTAMP,server_default=func.now(),onupdate=func.now())
    status_at = Column(TIMESTAMP,  nullable=True) 
    # Relationships 
    status = relationship("StatusModel")
    position = relationship("PositionModel") 
    groups = relationship("GroupsModel", secondary='user_groups', back_populates="users", cascade="save-update, delete")
    roles = relationship("RolesModel", secondary='user_roles', back_populates="users", cascade="save-update, delete")
    skills = relationship("SkillsModel", secondary='user_skills', back_populates="users", cascade="save-update, delete")
    deparment = relationship("DepartmentsModel", secondary='employees', back_populates="users", cascade="save-update, merge, delete")
    def __repr__(self): 
        return f"<User(id={self.id}" \
               f"email=\"{self.email}\"" \
               f"hashed_password=\"{self.hashed_password}\"" \
               f"is_active={self.is_active}"\
               f"name={self.name}"\
               f"last_name={self.last_name}"\
               f"patronymic={self.patronymic}"\
               f"login={self.login}"\
               f"phone={self.phone}"\
               f"inner_phone={self.inner_phone}"\
               f"photo_path={self.photo_path}"\
               F"status_id={self.status_id}"\
               f"date_employment_at={self.date_employment_at}"\
               f"date_dismissal_at={self.date_dismissal_at}"\
               f"created_at={self.created_at}"\
               f"updated_at={self.updated_at})>" 


