import math
from .super import SuperRepository, NotFoundError, Pagination
from app.database.models import DepartmentsModel, UserModel, EmployeesModel
from sqlalchemy.orm import Query
from typing import Iterator

# class User

class DeparmentsRepository(SuperRepository):

    base_model = DepartmentsModel

    def get_all(self) -> Iterator[DepartmentsModel]:
        with self.session_factory() as session:
            query = session.query(self.base_model).filter(self.base_model.is_active == True).order_by(self.base_model.id.asc()).all()
            if query is None:
                return []
            return query
    
    def get_struct(self, filter = None):
        with self.session_factory() as session:
            query = session.query(self.base_model)
            if filter is not None:
                query = query.join(EmployeesModel, EmployeesModel.department_id == self.base_model.id)\
                    .join(UserModel, UserModel.id == EmployeesModel.user_id)
                query = self.filter_params(query, filter)
                query = query.cte('cte', recursive=True)
                parnets = session.query(self.base_model).join(query, query.c.parent_department_id == self.base_model.id)
                recursive_q = query.union(parnets)
                q = session.query(recursive_q).all()
                items = {}
                for item in q:
                    deparment = DepartmentsModel(
                        id = item[0],
                        name = item[1],
                        parent_department_id = item[2],
                        is_parent = item[4]
                    )
                    items[item[0]] = deparment
                new_items = []
                for item in items:
                    new_items.append(items[item])
                items = new_items
                del new_items
            else:
                items = query.filter(self.base_model.is_active == True).order_by(self.base_model.id.asc()).all()
            return items
    def get_by_id(self, department_id: int) -> DepartmentsModel:
        return super().get_by_id(department_id)

    def filter_params(self, query, filter) -> Query:
        if filter['fio'] != None:  
            fio = filter['fio']
            query = query.filter(EmployeesModel.name.ilike(f'%{fio}%'))
        if len(filter['deparment']) != 0:
            query = query.filter(EmployeesModel.department_id.in_(filter['deparment']))
        if len(filter['position']) != 0:
            query = query.filter(UserModel.position_id.in_(filter['position']))
        if len(filter['status']) != 0:
            query = query.filter(UserModel.status_id.in_(filter['status']))
        if filter['phone'] != None:
            phone = filter['phone']
            query = query.filter(UserModel.inner_phone.ilike(f'%{phone}%'))
        return query

    def get_user_deparments(self, filter, limit: int, page: int):
        with self.session_factory() as session:
            offset = 0
            if page <= 1:
                page = 0
            if  page > 0:
                offset = (limit * page)
            employees = session.query(EmployeesModel).join(UserModel, UserModel.id == EmployeesModel.user_id)
            employees = self.filter_params(employees, filter).order_by(EmployeesModel.id.asc()).limit(limit).offset(offset).all()
            pagination = self.get_pagination(filter=filter, session=session, size=limit, page=page)
            pagination['employees'] = employees
            return pagination
    
    def get_pagination(self, filter, session, size: int, page: int):
        count_items = session.query(EmployeesModel)
        count_items = self.filter_params(count_items, filter).count()
        total_page = math.floor(count_items / size)
        return {
            "pagination": Pagination(
                total_page = total_page,
                total_count = count_items,
                page=page + 1,
                size=size
            )
        }
            



    def add(self, params):
        with self.session_factory() as session:
            self.find_depratment_by_name(params.name, session)
            
            if params.source_department == 0:
                params.source_department = None
            else:
                parent = self.find_deprment_by_id(params.source_department, session=session)
                parent.is_parent = True
                session.add(parent)
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
            current = self.find_deprment_by_id(id, session=session)
            if params.source_department == 0:
                params.source_department = None
            else:
                if current.parent_department_id != params.source_department:
                    new_parent = self.find_deprment_by_id(params.source_department, session=session)
                    new_parent.is_parent = True
                    session.add(new_parent)
                    if current.parent_department_id is not None:
                        old_parent = self.find_deprment_by_id(current.parent_department_id, session)
                        childs = session.query(self.base_model).filter(self.base_model.parent_department_id == current.parent_department_id).all()
                        count = 0
                        for child in childs:
                            if child.id != id:
                                count += 1
                        if count == 0:
                            old_parent.is_parent = False
                            session.add(old_parent)
            current.name = params.name
            current.parent_department_id = params.source_department
            self.__deparment_clear_employee(id, session=session)
            self.__add_employee(params=params, session=session,id=id)
            session.commit()
            return current

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

    def find_deprment_by_id(self, id, session) -> DepartmentsModel:
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
        