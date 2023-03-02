from app.kernel.database import Base
from sqlalchemy import Column ,BIGINT, SMALLINT, TIMESTAMP, ForeignKey, TIME
from sqlalchemy.orm import relationship

class StatusHistoryModel(Base):
    __tablename__ = "status_history"

    id = Column(BIGINT, primary_key=True)
    user_id = Column(BIGINT, ForeignKey("users.id", onupdate="CASCADE"))
    status_id = Column(SMALLINT, ForeignKey("status_users.id", onupdate="CASCADE"))
    update_at = Column(TIMESTAMP)
    time_at = Column(TIME)
    user = relationship("UserModel", back_populates="status_history")
    status = relationship("StatusModel")
    def __repr__(self) -> str:
        return f'UsersStatus<(id={self.id}, user_id={self.user_id}, status_id={self.status_id}, update_at={self.update_at})>'