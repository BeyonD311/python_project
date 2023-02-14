from .super import SuperRepository, NotFoundError
from app.database import EmployeesModel, DepartmentsModel, UserModel


class EmployeesRepository(SuperRepository):
    base_model = EmployeesModel

    def add(self, params):
        with self.session_factory() as session:
            users_find = self.get_users(params=params, session=session)
            if params.director_user_id not in users_find:
                raise NotFoundError("director_user_id not found")
            
                

    def update(self):
        pass
    
    def get_users(self, params, session):
        if params.deputy_head_id != None:
            users_id = [params.director_user_id, *params.deputy_head_id]
        else:
            users_id = [params.director_user_id]
            
        users = {}
        query = session.query(UserModel).filter(UserModel.id != 0).filter(UserModel.id.in_(users_id)).all()

        for user in query:
            users[user.id] = user.fio
        
        return users