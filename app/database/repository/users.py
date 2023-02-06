from .super import SuperRepository, NotFoundError
from app.database import UserModel as User, UserRoles, RolesModel

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

    def add(self, user_model: User) -> any:
       with self.session_factory() as session:
            user = user_model
            roles = session.query(RolesModel).filter(RolesModel.id.in_(user.roles_id)).all()
            [user.roles.append(r) for r in roles]
            session.add(user)
            session.commit()
            return user


class UserNotFoundError(NotFoundError):
    entity_name: str = "User"