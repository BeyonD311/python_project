from .super import SuperRepository, NotFoundError
from app.database.models import UserModel as User
from typing import Iterator

class UserRepository(SuperRepository):
    def get_all(self) -> Iterator[User]:
        with self.session_factory() as session:
            return session.query(User).all()

    def get_by_id(self, user_id: int) -> User:
        with self.session_factory() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundError(user_id)
            return user

    def delete_by_id(self, user_id: int) -> None:
        with self.session_factory() as session:
            entity: User = session.query(User).filter(User.id == user_id).first()
            if not entity:
                raise UserNotFoundError(user_id)
            session.delete(entity)
            session.commit()

    def add(self, email: str, password: str, is_active: bool = True, user_name: str = "test") -> User:
        with self.session_factory() as session:
            user = User(email=email, hashed_password=password, is_operator=is_active, user_name = user_name)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

class UserNotFoundError(NotFoundError):
    entity_name: str = "User"