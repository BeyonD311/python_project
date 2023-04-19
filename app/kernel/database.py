import logging
from contextlib import contextmanager, AbstractContextManager
from typing import Callable

from sqlalchemy import create_engine, orm, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
# Для наследования в Моделях
Base = declarative_base()

class Database:
    def __init__(self, db_url: str) -> None:
        print(db_url)
        self._engine = create_engine(db_url, echo=True, pool_size=10)
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
                expire_on_commit=False
            )
        )
    
    def create_database(self) -> None:
        Base.metadata.create_all(self._engine)
    
    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self._session_factory()
        self.event_listner(session=session)
        try:
            yield session
        except Exception:
            logger.exception("Session rollback because of exception")
            print("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()
            # if session.event == "after_commit":
            #     print('commit-------------------------------')
            #     session.close()
    def event_listner(self, session: Session):
        session.event = None
        @event.listens_for(session, "after_commit")
        def functest(session):
            session.event = "after_commit"
