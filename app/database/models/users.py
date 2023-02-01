from sqlalchemy import Column, String, Boolean, Integer, VARCHAR
from app.kernel.database import Base

class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    name = Column(String)
    last_name = Column(String)
    patronymic = Column(String)
    user_name = Column(String)
    is_operator = Column(Boolean, default=False)
    def __repr__(self):
        return f"<User(id={self.id}, " \
               f"email=\"{self.email}\", " \
               f"hashed_password=\"{self.hashed_password}\", " \
               f"is_operator={self.is_operator})>"


