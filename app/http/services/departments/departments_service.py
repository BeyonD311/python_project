from app.database import DepartmentsRepository
from app.database import DepartmentsModel
from app.http.services.users import UserStatus
from app.http.services.users import UsersResponse
from pydantic import BaseModel
from pydantic import validator
from typing import List

class DepartmentParams(BaseModel):
    name: str
    source_department: int = None
    director_user_id: int = None
    deputy_head_id: List[int] = None

class Node(BaseModel):
    name:str
    id: int
    child: List = []

class Filter(BaseModel):
    fio: str = None
    department: list = None
    position: list = None
    status: list = None
    phone: str = None

    @validator('fio')
    def check_fio(cls, v):
        if v is "":
            return None
        return v
    @validator('phone')
    def check_phone(cls, v):
        if v is "":
            return None
        return v
class DepartmentResponse(BaseModel):
    nodes: Node

class DepartmentsService:

    def __init__(self, repository: DepartmentsRepository) -> None:
        self._repository: DepartmentsRepository = repository

    def get_all(self):
        return self._repository.get_all()

    """ Получение структуры с фильтрами """
    def __check_filter(self, filter: set):
        flag = False
        for param in filter:
            value = filter[param]
            if value != None:
                flag = True
                break
        if flag == False:
            filter = None
        return filter


    def get_employees(self, filter: Filter):
        items = self._repository.get_employees(filter.dict())
        res = []
        for i, item in items.items():
            if item.parent_department_id != None: 
                continue
            if item.is_parent:
                self.find_child(items, item)
            res.append(item)
        return res

    def get_users_department(self, filter: dict, page:int, size: int):
        filter = self.__check_filter(filter)
        result = self._repository.get_user_departments(filter=filter, limit=size, page=page)
        users = []
        for employee in result['employees']:
            user = UsersResponse(
                id = employee.id,
                fio = employee.fio,
                head_of_department=employee.head_of_department,
                inner_phone=employee.inner_phone,
            )
            if employee.position != None:
                user.position = employee.position.name
            if employee.department != None:
                user.department = employee.department.name
            if employee.status != None:
                user.status=UserStatus(
                    status_id=employee.id,
                    status_at=employee.status_at,
                    color=employee.status.color,
                    status=employee.status.alter_name
                )
            users.append(user)
        result['employees'] = users
        return result

    def get_by_id(self, id):
        return self._repository.get_by_id(id)

    def add(self, params: DepartmentParams):
        return self._repository.add(params)
    
    def update(self, params: DepartmentParams, id: int):
        return self._repository.update(id, params)

    def delete(self, id):
        self._repository.delete_by_id(id)

    def find_child(self, items: List[DepartmentsModel], parent: DepartmentsModel):
        item: DepartmentsModel
        for item  in items:
            item = items[item]
            if parent.id == item.parent_department_id:
                if item.is_parent:
                    parent.child.append(self.find_child(items ,item))
                else:
                    parent.child.append(item)
        return parent