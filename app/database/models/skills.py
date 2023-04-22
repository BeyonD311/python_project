from sqlalchemy import String, Column, BIGINT
from sqlalchemy.orm import relationship
from app.kernel.database import Base

class SkillsModel(Base):
    __tablename__ = "skills"

    id = Column(BIGINT, primary_key=True)
    name = Column(String)
    users = relationship("UserModel", secondary="user_skills", back_populates = "skills")

    def __repr__(self) -> str:
        return f"<Skills(id={self.id}, name={self.name})>" 