from sqlalchemy import Boolean, Column, ForeignKey
from app.kernel.database import Base

class UserRoles(Base):

    __tablename__ = "user_roles"

    user_id = Column(ForeignKey("user.id"))
    role_id = Column(ForeignKey("roles.id"))

    def __repr__(self) -> str:
        return "<UserRoles("\
            f"user_id={self.user_id}"\
            f"role_id={self.role_id}"\
            ")>"
            