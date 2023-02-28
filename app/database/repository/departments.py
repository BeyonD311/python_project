import math
from pydantic import BaseModel
from .super import SuperRepository, NotFoundError, Pagination
from app.database.models import DepartmentsModel
from app.database.models import UserModel
from app.database.models import HeadOfDepatment
from sqlalchemy.orm import Query
from sqlalchemy.orm import Session
from typing import Iterator

class Depratment(BaseModel):
    id: int
    name: str = None
    parent_department_id: int = None
    is_parent: bool

class DeparmentsRepository(SuperRepository):

    base_model = DepartmentsModel

    def get_all(self) -> Iterator[DepartmentsModel]:
        with self.session_factory() as session:
            query = session.query(self.base_model).filter(self.base_model.is_active == True).order_by(self.base_model.id.asc()).all()
            if query is None:
                return []
            return query
    
    def get_struct(self, filter = None) -> Depratment:
        with self.session_factory() as session:
            query = session.query(self.base_model)
            if filter is not None:
                query = query.join(UserModel, UserModel.department_id == self.base_model.id)
                query = self.filter_params(query, filter)
                query = query.cte('cte', recursive=True)
                parnets = session.query(self.base_model).join(query, query.c.parent_department_id == self.base_model.id)
                recursive_q = query.union(parnets)
                q = session.query(recursive_q).all()
                items = {}
                for item in q:
                    deparment = Depratment(
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
    # Параметры фильтра
    def filter_params(self, query, filter) -> Query:
        if filter['fio'] != None:  
            fio = filter['fio']
            query = query.filter(UserModel.fio.ilike(f'%{fio}%'))
        if len(filter['deparment']) != 0:
            query = query.filter(UserModel.department_id.in_(filter['deparment']))
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
            employees = session.query(UserModel).filter(UserModel.id != 0)
            employees = self.filter_params(employees, filter).order_by(UserModel.id.asc())
            if page == 0:
                page = 1
            pagination = self.get_pagination(query = employees, size=limit, page=page)
            pagination['employees'] = employees.limit(limit).offset(offset).all()
            return pagination
    
    def get_pagination(self, query, size: int, page: int):
        count_items = query.count()
        total_page = math.ceil(count_items / size)
        return {
            "pagination": Pagination(
                total_page = total_page,
                total_count = count_items,
                page=page,
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
            self.__deparment_update_employee(id, session=session, params=params)
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
        query = session.query(UserModel).filter(UserModel.id != 0).filter(UserModel.department_id == deparment_id).all()
        for employee in query:
                result[employee.user_id] = employee
        return result

    def find_deprment_by_id(self, id, session) -> DepartmentsModel:
        query = session.query(self.base_model).filter(self.base_model.id == id).first()
        if query is None:
            raise NotFoundError("department exists")
        return query
    
    def __add_employee(self, params, session: Session ,id: int):
        if params.director_user_id is not None:
            session.add(HeadOfDepatment(
                    department_id=id,
                    head_of_depatment_id=params.director_user_id
                ))
        for user_id in params.deputy_head_id:
            session.add(HeadOfDepatment(
                department_id=id,
                deputy_head_id=user_id
            ))
    
    def __deparment_update_employee(self, id, params, session: Session):
        departments = session.query(HeadOfDepatment).filter(HeadOfDepatment.department_id == id).all()
        head_employees_deprament = None
        for department in departments:
            if department.head_of_depatment_id != None:
                head_employees_deprament = department
            else:
                session.delete(department)
        del departments
        if head_employees_deprament != None and params.director_user_id != None:
            if params.director_user_id != head_employees_deprament.head_of_depatment_id:
                head_employees_deprament.head_of_depatment_id = params.director_user_id
                session.add(head_employees_deprament)
        elif head_employees_deprament == None and params.director_user_id != None:
            session.add(HeadOfDepatment(
                    department_id=id,
                    head_of_depatment_id=params.director_user_id
                ))
        for user_id in params.deputy_head_id:
            session.add(HeadOfDepatment(
                department_id=id,
                deputy_head_id=user_id
            ))
