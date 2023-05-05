from .super import SuperRepository
from app.database.models import (
    PositionModel, UserModel
)
from typing import Iterator
from pydantic import BaseModel

class User(BaseModel):
    fio: str
    inner_phone: int
    position: int
    is_selected: bool = False

class PositionRepository(SuperRepository):
    base_model = PositionModel

    def get_all(self) -> Iterator[PositionModel]:
        return super().get_all()

    def get_users_by_position(self, id: int, fio: str) -> PositionModel:
        with self.session_factory() as session:
            users = session.query(UserModel).filter(UserModel.position_id == id)
            if fio != "":
                users = users.filter(UserModel.fio.ilike(f"%{fio}%"))
            users = users.order_by(UserModel.id.asc()).all()
            result = []
            session.commit()
            user: UserModel
            for user in users:
                new_user = {
                    "fio": user.fio
                }
                for inner_phone in user.inner_phone:
                    if inner_phone.is_registration and inner_phone.is_default:
                        new_user['inner_phone'] = inner_phone.phone_number
                if 'inner_phone' in new_user:
                    result.append(User(
                        fio=new_user['fio'],
                        inner_phone=new_user['inner_phone'],
                        position=id
                    ))
                del new_user
            return result
    

    def add(self, arg):
        ...

    def update(self):
        ...


__all__ = ('PositionRepository')