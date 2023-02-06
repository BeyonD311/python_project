from .super import SuperRepository, NotFoundError
from app.database.models.users import UserModel as User


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
           
           add = session.add(user_model)
           print(add)
           session.commit()
           session.flush(user_model)

class UserNotFoundError(NotFoundError):
    entity_name: str = "User"