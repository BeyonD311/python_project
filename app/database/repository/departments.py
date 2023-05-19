import math
from datetime import datetime
from pydantic import BaseModel
from .super import SuperRepository, NotFoundError, Pagination, ExistsException
from app.database.models import DepartmentsModel
from app.database.models import InnerPhone
from app.database.models import UserModel
from app.database.models import HeadOfDepartment
from app.database.models import PositionModel
from app.database.models import StatusModel
from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy.orm import Query
from sqlalchemy.orm import Session
from typing import Iterator


class UserStatus(BaseModel):
    status: str = None
    status_id: int = None
    status_at: datetime = None
    color: str = None

class Department(BaseModel):
    id: int
    name: str = None
    parent_department_id: int = None
    is_parent: bool
    employees: list = []
    child: list = []
    head: list = []
    deputy_head: list = []

class UsersResponse(BaseModel):
    id: int = None
    fio: str = None
    inner_phone: str = None
    position: str = None
    is_head_of_department: bool = False
    status: dict = None

def new_user_response(params) -> UsersResponse:
    """ Создание UserResonse """
    return UsersResponse(
        id = params[4],
        fio = params[5],
        inner_phone = params[6],
        position = params[12],
        is_head_of_department=bool(params[8]),
        status={
            "id": params[11],
            "status": params[10],
            "status_id": params[7],
            "color": params[9]
        }
    )

class DepartmentsRepository(SuperRepository):

    base_model = DepartmentsModel

    def get_all(self) -> Iterator[DepartmentsModel]:
        with self.session_factory() as session:
            query = session.query(self.base_model).filter(self.base_model.is_active == True).order_by(self.base_model.id.asc()).all()
            if query is None:
                return []
            return query
    
    def get_employees(self, filter = None) -> Department:  # TODO: проверить DISTINCT users
        with self.session_factory() as session:
            query = session.query(
                self.base_model.id.label("department_id"),
                self.base_model.name.label("department_name"),
                self.base_model.parent_department_id.label("department_parent"),
                self.base_model.is_parent.label("is_parent"),
                UserModel.id.label("user_id"),
                UserModel.fio.label("user_fio"),
                UserModel.status_at.label("status_at"),
                HeadOfDepartment.head_of_department_id.label("head_of_department_id"),
                StatusModel.color.label("status_color"),
                StatusModel.name.label("status_name"),
                StatusModel.id.label("status_id"),
                PositionModel.name.label("position"),
                InnerPhone.phone_number.label("user_inner_phone"),
                HeadOfDepartment.deputy_head_id.label("deputy_head_id")
            )\
            .join(UserModel, UserModel.department_id == self.base_model.id, isouter=True)\
            .join(HeadOfDepartment, or_(HeadOfDepartment.head_of_department_id == UserModel.id, HeadOfDepartment.deputy_head_id == UserModel.id), isouter=True)\
            .join(StatusModel, StatusModel.id == UserModel.status_id, isouter=True)\
            .join(PositionModel, PositionModel.id == UserModel.position_id, isouter=True)\
            .join(InnerPhone, and_(InnerPhone.user_id == self.base_model.id, InnerPhone.is_default == True, InnerPhone.is_registration == True), isouter=True)
            query = self.filter_params(query=query, filter=filter)
            result = {}
            parents = []
            query = session.execute(self.__query_employees(filter))
            for res in query.all():
                if res[2] is not None:
                    parents.append(res[2])
                if res[0] not in result:
                    result[res[0]] = Department(
                        id = res[0],
                        name = res[1],
                        parent_department_id=res[2],
                        is_parent=res[3]
                    )
                if res[4] is not None:
                    if res[4] is not result[res[0]].employees:
                        if res[4] == 0:
                            continue
                        if bool(res[8]):
                            result[res[0]].deputy_head.append(new_user_response(res))
                        elif bool(res['deputy_head_id']):
                            result[res[0]].head.append(new_user_response(res))
                        else:
                            result[res[0]].employees.append(new_user_response(res))
            #TODO возможно понадобиться для работы если нет то удалить
            """ Получем родителей рекурсивно """
            parents = set(parents)
            query = session.query(
                self.base_model.id,
                self.base_model.name,
                self.base_model.parent_department_id,
                self.base_model.is_parent
            ).filter(self.base_model.id.in_(parents)).cte('cte', recursive=True)
            parents = session.query(
                self.base_model.id,
                self.base_model.name,
                self.base_model.parent_department_id,
                self.base_model.is_parent
            ).join(query, query.c.parent_department_id == self.base_model.id)
            recursive_q = query.union(parents)
            query = session.query(recursive_q).all()
            for res in query:
                if res[0] not in result:
                    result[res[0]] = Department(
                            id = res[0],
                            name = res[1],
                            parent_department_id=res[2],
                            is_parent=res[3]
                        )
            return result
        
    def get_by_id(self, department_id: int) -> DepartmentsModel:
        return super().get_by_id(department_id)
    # Параметры фильтра
    def filter_params(self, query, filter) -> Query:
        filter_res = " and "
        params = []
        if filter['fio'] != None:
            fio = filter['fio']
            params.append(f"users.fio ilike '%{fio}%'")
            query = query.filter(UserModel.fio.ilike(f'%{fio}%'))
        if len(filter['department']) != 0:
            department = ','.join(filter['department'])
            params.append(f"departments.id in ({department})")
            query = query.filter(self.base_model.id.in_(filter['department']))
        if len(filter['position']) != 0:
            position = ','.join(filter['position'])
            params.append(f"users.position_id in ({position})")
            query = query.filter(UserModel.position_id.in_(filter['position']))
        if len(filter['status']) != 0:
            status = ','.join(filter['status'])
            params.append(f"users.status_id in ({status})")
            query = query.filter(UserModel.status_id.in_(filter['status']))
        if filter['phone'] != None:
            phone = filter['phone'].replace(' ', ',').replace(',,', ',')
            params.append(f"inner_phones.phone_number in ({phone})")
            query = query.filter(InnerPhone.phone_number.in_(phone.split(',')))
        return query

    def __filter_params(self, filter):
        params = []
        if filter['fio'] != None:  
            fio = filter['fio']
            params.append(f"users.fio ilike '%{fio}%'")
        if len(filter['department']) != 0:
            department = ','.join(filter['department'])
            params.append(f"departments.id in ({department})")
        if len(filter['position']) != 0:
            position = ','.join(filter['position'])
            params.append(f"users.position_id in ({position})")
        if len(filter['status']) != 0:
            status = ','.join(filter['status'])
            params.append(f"users.status_id in ({status})")
        if filter['phone'] != None:
            phone = filter['phone'].replace(' ', ',').replace(',,', ',')
            params.append(f"inner_phones.phone_number in ({phone})")
        if len(params) > 0:
            return "where " + " and ".join(params)
        return ""

    def get_user_departments(self, filter, limit: int, page: int):
        with self.session_factory() as session:
            offset = 0
            if page <= 1:
                page = 0
            if  page > 0:
                if page > 1:
                    page -= 1
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
            self.find_department_by_name(params.name, session)
            
            if params.source_department == 0:
                params.source_department = None
            else:
                parent = self.find_department_by_id(params.source_department, session=session)
                parent.is_parent = True
                session.add(parent)
            department = DepartmentsModel(
                name = params.name,
                parent_department_id = params.source_department
            )

            session.add(department)
            session.commit()

            if department.id is None:
                description = "Невозможно создать департамент"
                raise NotFoundError(entity_id=department.id, entity_description=description)
            
            try:
                self.__add_employee(params=params, session=session, id=department.id)
            except Exception:
                session.delete(department)
            finally:
                session.commit()
                
            return department
            
    def update(self, id, params):
        with self.session_factory() as session:
            current = self.find_department_by_id(id, session=session)
            if params.source_department == 0:
                params.source_department = None
            else:
                if current.parent_department_id != params.source_department:
                    new_parent = self.find_department_by_id(params.source_department, session=session)
                    new_parent.is_parent = True
                    session.add(new_parent)
                    if current.parent_department_id is not None:
                        old_parent = self.find_department_by_id(current.parent_department_id, session)
                        chields = session.query(self.base_model).filter(self.base_model.parent_department_id == current.parent_department_id).all()
                        count = 0
                        for child in chields:
                            if child.id != id:
                                count += 1
                        if count == 0:
                            old_parent.is_parent = False
                            session.add(old_parent)
            current.name = params.name
            current.parent_department_id = params.source_department
            self.__department_update_employee(id, session=session, params=params)
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

    
    def delete_by_id(self, department_id: int):
        with self.session_factory() as session :
            department = session.query(self.base_model).filter(self.base_model.id == department_id).first()
            if department is None:
                session.commit()
                raise NotFoundError(entity_id=department.id, entity_description="Департамент не обнаружен")
            session.delete(department)
            session.commit()
            
    def find_department_by_name(self, name: str, session):
        query = session.query(self.base_model).filter(self.base_model.name.ilike(f"%{name}%")).first()
        if query is not None:
            description = f"Уже существует департамент с именем '{name}'."
            raise ExistsException(item=name, entity_description=description)

    def find_employee(self, department_id: int, session):
        result = {}
        query = session.query(UserModel).filter(UserModel.id != 0).filter(UserModel.department_id == department_id).all()
        for employee in query:
            result[employee.user_id] = employee
        return result

    def find_department_by_id(self, id, session) -> DepartmentsModel:
        query = session.query(self.base_model).filter(self.base_model.id == id).first()
        if query is None:
            description = f"Не существует департамент с ID={id}."
            raise NotFoundError(entity_id=id, entity_description=description)
        return query
    
    def __add_employee(self, params, session: Session ,id: int):
        if params.director_user_id is not None:
            session.add(HeadOfDepartment(
                    department_id=id,
                    head_of_department_id=params.director_user_id
                ))
        for user_id in params.deputy_head_id:
            session.add(HeadOfDepartment(
                department_id=id,
                deputy_head_id=user_id
            ))
    
    def __department_update_employee(self, id, params, session: Session):
        departments = session.query(HeadOfDepartment).filter(HeadOfDepartment.department_id == id).all()
        head_employees_department = None
        for department in departments:
            if department.head_of_department_id != None:
                head_employees_department = department
            else:
                session.delete(department)
        del departments
        if head_employees_department != None and params.director_user_id != None:
            if not self.get_users(params, session):
                description = f"Не существует пользователь с ID={params.director_user_id}."
                raise NotFoundError(entity_id=id, entity_description=description)
            if params.director_user_id != head_employees_department.head_of_department_id:
                head_employees_department.head_of_department_id = params.director_user_id
                session.add(head_employees_department)
        elif head_employees_department == None and params.director_user_id != None:
            if not self.get_users(params, session):
                description = f"Не существует пользователь с ID={params.director_user_id}."
                raise NotFoundError(entity_id=id, entity_description=description)
            session.add(HeadOfDepartment(
                department_id=id,
                head_of_department_id=params.director_user_id
            ))
        for user_id in params.deputy_head_id:
            session.add(HeadOfDepartment(
                department_id=id,
                deputy_head_id=user_id
            ))


    def __query_employees(self, filter):
        query1 = self.__query_select_fields(False) + " " + self.__query_join(True) + " " + self.__filter_params(filter)
        query2 = self.__query_select_fields(True) + " " + self.__query_join() + " " + self.__filter_params(filter)
        return f"select templ.department_id, templ.department_name, templ.department_parent, templ.is_parent, templ.user_id,"\
                " templ.user_fio, templ.user_inner_phone, templ.status_at, "\
                " templ.head_of_department_id, templ.status_color, templ.status_name, templ.status_id, position, deputy_head_id"\
                f"  from ({query1} union {query2}) templ where 1=1 "
        

    def __query_select_fields(self, fake = False):
        fields = ""
        if fake == False:
            fields = f" head_of_departments.head_of_department_id AS head_of_department_id,"\
                    f" head_of_departments.deputy_head_id AS deputy_head_id,"
        else:   
            fields = f"int'0' AS head_of_department_id,"\
                    f"int'0' AS deputy_head_id,"

        select = f"select departments.id AS department_id,"\
                f"departments.name AS department_name,"\
                f"departments.parent_department_id AS department_parent,"\
                f"departments.is_parent AS is_parent,"\
                f"users.id AS user_id,"\
                f"users.fio AS user_fio,"\
                f"users.status_at AS status_at,"\
                f"{fields}"\
                f"status_users.color AS status_color,"\
                f"status_users.name AS status_name,"\
                f"status_users.id AS status_id,"\
                f"position.name AS position,"\
                f"inner_phones.phone_number AS user_inner_phone from departments"
        return select

    def __query_join(self, head = False):
        if head:
            head = f"LEFT OUTER JOIN head_of_departments ON head_of_departments.department_id = departments.id "\
                   f"JOIN users ON users.id = head_of_departments.head_of_department_id or users.id = head_of_departments.deputy_head_id "
        else:
            head = f"JOIN users ON users.department_id = departments.id"
        
        join = f"{head} "\
               f"LEFT OUTER JOIN status_users ON status_users.id = users.status_id "\
               f"LEFT OUTER JOIN position ON position.id = users.position_id "\
               f"LEFT OUTER JOIN inner_phones ON inner_phones.user_id = users.id AND inner_phones.is_default = true AND inner_phones.is_registration = true "
        return join