import datetime
from .super import SuperRepository, NotFoundError
from app.database import UserModel as User
from typing import Iterator

class UserRepository(SuperRepository):
    base_model = User
    
    def get_all(self, offset, limit) -> dict[User]:
        with self.session_factory() as session:
            result = self.get_pagination(session, offset, limit)
            result['items'] = session.query(self.base_model).limit(limit).offset(offset).all()
            return result

    def get_by_id(self, user_id: int) -> User:
        return super().get_by_id(user_id)

    def update(self):
        return "this update"

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