from .super import SuperRepository, NotFoundError
from app.database.models import DepartmentsModel, UserModel, EmployeesModel
from typing import Iterator

# class User

class DeparmentsRepository(SuperRepository):

    base_model = DepartmentsModel

    def get_all(self) -> Iterator[DepartmentsModel]:
        return super().get_all()
    def get_by_id(self, department_id: int) -> DepartmentsModel:
        return super().get_by_id(department_id)
    def add(self, params):
        with self.session_factory() as session:
            users_find = self.get_users(params=params, session=session)
            print("----------------------")
            print(users_find)
            print("----------------------")
            if params.director_user_id not in users_find:
                raise NotFoundError("director_user_id not found")
            self.find_depratment_by_name(params.name, session)
            employees = self.find_employee(users_find, session)
            employee_head: EmployeesModel = employees[params.director_user_id]
            employee_head.head_of_depatment = True
            session.add(employee_head)
            del employees[params.director_user_id]
            for employe in employees:
                value:EmployeesModel = employees[employe]
                value.deputy_head = True
            

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
    
    def find_depratment_by_name(self, name: str, session):
        query = session.query(self.base_model).filter(self.base_model.name.ilike(f"%{name}%")).first()
        if query is not None:
            raise NotFoundError("department exists")

    def find_employee(self, deparment_id: int, session):
        result = {}
        query = session.query(EmployeesModel).filter(EmployeesModel.id != 0).filter(EmployeesModel.department_id.in_(deparment_id)).all()
        for employee in query:
                result[employee.user_id] = employee
        return result