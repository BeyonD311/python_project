from app.kernel.database import Base
from sqlalchemy import Column 
from sqlalchemy import BIGINT
from sqlalchemy import SMALLINT
from sqlalchemy import TIMESTAMP
from sqlalchemy import ForeignKey
from sqlalchemy import TIME
from sqlalchemy import Boolean
from sqlalchemy.orm import relationship

class StatusHistoryModel(Base):
    __tablename__ = "status_history"

    id = Column(BIGINT, primary_key=True) 
    user_id = Column(BIGINT, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"))
    status_id = Column(SMALLINT, ForeignKey("status_users.id", onupdate="CASCADE", ondelete="SET NULL"))
    update_at = Column(TIMESTAMP)
    time_at = Column(TIME, nullable=True)
    is_active = Column(Boolean, default=True)
    users = relationship("UserModel", back_populates="status_history", cascade="all, delete")
    status = relationship("StatusModel")
    def __repr__(self) -> str:
        return f'UsersStatus<(id={self.id}, user_id={self.user_id}, status_id={self.status_id}, update_at={self.update_at})>'  