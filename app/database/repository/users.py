from http.client import HTTPException

from pydantic import EmailStr
from starlette import status

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

    def check_user_email(self, user_email: EmailStr) -> User:
        with self.session_factory() as session:
            var: bool = True
            user = session.query(User).filter(User.email == EmailStr(user_email.lower())).first()
            if not user:
                var = False
                # raise EmailNotFoundError(user_email)
            return var

    def check_user_name(self, user_name: str) -> User:
        with self.session_factory() as session:
            var: bool = True
            user = session.query(User).filter(User.name == user_name).first()
            if not user:
                var = False
                # raise UserNotFoundError(user_name)
            return var

    def check_user(self, user_login: str, is_email: bool) -> User:
        with self.session_factory() as session:
            var: bool = True
            if is_email:
                user = session.query(User).filter(User.email == EmailStr(user_login.lower())).first()
            else:
                user = session.query(User).filter(User.name == user_login).first()
        if user is None:
            var = False
            # raise EmailNotFoundError(user_email)
        return var

    def delete_by_id(self, user_id: int) -> None:
        with self.session_factory() as session:
            entity: User = session.query(User).filter(User.id == user_id).first()
            if not entity:
                raise UserNotFoundError(user_id)
            session.delete(entity)
            session.commit()

    def add(self, name: str, email: EmailStr, password: str) -> User:
        with self.session_factory() as session:
            user = User(name=name, email=email, hashed_password=password)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def get_hashed_password(self, user_login: EmailStr, is_email: bool) -> User:
        with self.session_factory() as session:
            if is_email:
                user = session.query(User).filter(User.email == EmailStr(user_login.lower())).first()
            else:
                user = session.query(User).filter(User.name == user_login).first()
        return user.hashed_password

    def return_user_id(self, user_login: str, is_email: bool) -> User:
        with self.session_factory() as session:
            if is_email:
                user = session.query(User).filter(User.email == EmailStr(user_login.lower())).first()
            else:
                user = session.query(User).filter(User.name == user_login).first()
        return user.id


class UserNotFoundError(NotFoundError):
    entity_name: str = "User"

