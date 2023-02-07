import os
from .super import SuperRepository, NotFoundError
from app.database import UserModel as User, UserRoles, RolesModel
from sqlalchemy.exc import IntegrityError

class UserRepository(SuperRepository): 
    base_model = User
    
    def get_all(self, offset, limit) -> dict[User]:
        with self.session_factory() as session:
            result = self.get_pagination(session, offset, limit)
            result['items'] = session.query(self.base_model).limit(limit).offset(offset).all()
            return result

    def get_by_id(self, user_id: int) -> User:
        return super().get_by_id(user_id)

    def update(self, user_model: User):
        try:
            with self.session_factory() as session:
                user = user_model
                current = session.query(self.base_model).filter(self.base_model.id == user.id).first()
                if current is None:
                    raise IntegrityError("Пользователь не найден", "Пользователь не найден", "Пользователь не найден")
                for param in user.__dict__:
                    if param == '_sa_instance_state' or param == 'id' or param == 'roles_id':
                        continue
                    values = user.__dict__[param]
                    current.__setattr__(param, values)
                roles = session.query(RolesModel).filter(RolesModel.id.in_(user.roles_id)).all()
                current.roles.clear()
                [current.roles.append(r) for r in roles]
                session.add(current)
                session.commit()
                user.__delattr__("hashed_password")
                user.__delattr__("password")
                return user
        except IntegrityError as e:
            os.remove(user_model.photo_path)
            return False, e

    def add(self, user_model: User) -> any:
        try:
            with self.session_factory() as session:
                user = user_model
                roles = session.query(RolesModel).filter(RolesModel.id.in_(user.roles_id)).all()
                [user.roles.append(r) for r in roles]
                session.add(user)
                session.commit()
                session.flush()
                user.__delattr__("hashed_password")
                user.__delattr__("password")
                return user
        except IntegrityError as e:
            if user_model.photo_path is not None:
                os.remove(user_model.photo_path)
            return False, e

class UserNotFoundError(NotFoundError):
    entity_name: str = "User"