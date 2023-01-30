from sqlalchemy import Column, String, Boolean, Integer
from app.kernel.database import Base


class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String)
    name = Column(String(50))
    last_name = Column(String(50))
    patronymic = Column(String(50))
    user_name = Column(String(50))
    is_operator = Column(Boolean, default=False)

    def __repr__(self):
        return f"<User(id={self.id}, " \
               f"email=\"{self.email}\", " \
               f"hashed_password=\"{self.hashed_password}\", " \
               f"name=\"{self.name}\", " \
               f"last_name=\"{self.last_name}\", " \
               f"patronymic=\"{self.patronymic}\", " \
               f"user_name=\"{self.user_name}\", " \
               f"is_operator={self.is_operator})>"

