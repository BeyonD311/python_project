import datetime
from .super import SuperRepository, NotFoundError
from app.database import UserModel as User
from typing import Iterator

class UserRepository(SuperRepository):
    def get_all(self, start: int = 0, end: int = 1) -> Iterator[User]:
        with self.session_factory() as session:
            return session.query(User).slice(start, end).all()

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

    def add(self, 
    email: str, 
    password: str, 
    login: str,
    name: str, 
    last_name: str, 
    department_id: int,
    date_employment_at: datetime.datetime,
    phone: str = "",
    patronymic: str = "",
    is_operator: bool = False,
    is_active: bool = True,
    inner_phone: int = None, 
    photo_path: str = None,
    date_dismissal_at: datetime.datetime = None,
    ) -> User:

        with self.session_factory() as session:
            user = User(
                email = email, 
                password = password, 
                hashed_password = password, 
                login = login,
                name = name,
                last_name = last_name,
                department_id = department_id,
                date_employment_at = date_employment_at,
                phone = phone,
                patronymic = patronymic,
                is_operator = is_operator,
                is_active = is_active,
                inner_phone = inner_phone,
                photo_path = photo_path,
            )
            if date_dismissal_at is not None:
                user.date_dismissal_at = date_dismissal_at
            session.add(user)
            session.commit()
            session.refresh(user) 
            return user

class UserNotFoundError(NotFoundError):
    entity_name: str = "User"