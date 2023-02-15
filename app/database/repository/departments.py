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
            self.find_depratment_by_name(params.name, session)
            
            if params.source_department == 0:
                params.source_department = None
            else:
                self.find_deprment_by_id(params.source_department, session=session)
            department = DepartmentsModel(
                name = params.name,
                parent_department_id = params.source_department
            )

            session.add(department)
            session.commit()

            if department.id is None:
                raise NotFoundError("Not create")
            
            try:
                self.__add_employee(params=params, session=session, id=department.id)
            except Exception:
                session.delete(department)
            finally:
                session.commit()
                
            return department
            

    def update(self, id, params):
        with self.session_factory() as session:
            self.find_deprment_by_id(id, session=session)
            if params.source_department == 0:
                params.source_department = None
            else:
                self.find_deprment_by_id(params.source_department, session=session)
            self.__deparment_clear_employee(id, session=session)
            self.__add_employee(params=params, session=session,id=id)
            session.commit()

    def get_users(self, params, session):
        if params.deputy_head_id != None:
            users_id = [params.director_user_id, *params.deputy_head_id]
        else:
            users_id = [params.director_user_id]
        users = {}
        query = session.query(UserModel).filter(UserModel.id != 0).filter(UserModel.id.in_(users_id)).all()
        for user in query:
            users[user.id] = user
        return users
    
    def find_depratment_by_name(self, name: str, session):
        query = session.query(self.base_model).filter(self.base_model.name.ilike(f"%{name}%")).first()
        if query is not None:
            raise NotFoundError("department exists")

    def find_employee(self, deparment_id: int, session):
        result = {}
        query = session.query(EmployeesModel).filter(EmployeesModel.id != 0).filter(EmployeesModel.department_id == deparment_id).all()
        for employee in query:
                result[employee.user_id] = employee
        return result

    def find_deprment_by_id(self, id, session):
        query = session.query(self.base_model).filter(self.base_model.id == id).first()
        if query is None:
            raise NotFoundError("department exists")
        return query
    def __create_employee(self, params):
        return EmployeesModel( 
            name = params['name'],
            department_id = params['department_id'],
            user_id = params['user_id'],
            head_of_depatment = params['head_of_depatment'],
            deputy_head = params['deputy_head']
        )

    def __deparment_clear_employee(self, depatment_id, session):
        employees = self.find_employee(depatment_id, session)
        for employe in employees:
            employe = employees[employe]
            session.delete(employe)
        session.commit()

    def __add_employee(self, params, session, id):
        users_find = self.get_users(params=params, session=session)

        if params.director_user_id not in users_find:
            raise NotFoundError("director_user_id not found")

        employee_head: UserModel = users_find[params.director_user_id]
        session.add(self.__create_employee({
            "name": employee_head.fio,
            "department_id": id,
            "user_id" : params.director_user_id,
            "head_of_depatment" :True,
            "deputy_head":False
        }))
        del users_find[params.director_user_id]
        for user in users_find:
            value = users_find[user]
            employee = self.__create_employee({
                "name": value.fio,
                "department_id": id,
                "user_id" : user,
                "head_of_depatment" :False,
                "deputy_head":True
            })
            session.add(employee)
        