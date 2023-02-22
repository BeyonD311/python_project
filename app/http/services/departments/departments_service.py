from app.database import DeparmentsRepository, DepartmentsModel
from pydantic import BaseModel
from typing import List, Iterator

class EmployeeResponse(BaseModel):
    id: int
    fio: str
    is_head_of_depatment: bool
    status:str
    status_at: str
    inner_phone: str

class DepartmentParams(BaseModel):
    name: str
    source_department: int = None
    director_user_id: int
    deputy_head_id: List[int] = None

class Node(BaseModel):
    name:str
    id: int
    child: List = []

class DeparmentResponse(BaseModel):
    nodes: Node

class DepartmentsService:

    def __init__(self, repository: DeparmentsRepository) -> None:
        self._repository: DeparmentsRepository = repository
    def get_all(self):
        return self._repository.get_all()

    """ Получение структуры с фильтрами """
    def __check_filter(self, filter: set):
        flag = False
        for param in filter:
            v = filter[param]
            if v != None:
                flag = True
                break
        if flag == False:
            filter = None
        return filter


    def get_struct(self, filter: dict):
        # items = self._repository.get_all()
        items = self._repository.get_struct(self.__check_filter(filter))
        res = []
        for item in items:
            if item.parent_department_id != None: 
                continue
            node = Node(
                    name=item.name,
                    id=item.id
                )
            if item.is_parent:
                self.find_child(items, node)
            res.append(node)
        return res

    def get_users_deprtment(self, filter: dict, page:int, size: int):
        filter = self.__check_filter(filter)
        result = self._repository.get_user_deparments(filter=filter, limit=size, page=page)
        users = []
        employee
        for employee in result['employees']:
            users.append(EmployeeResponse(
                id = employee.id,
                fio = employee.name,
                is_head_of_depatment=employee.head_of_depatment,
                status=employee.user.status.name,
                status_at=employee.user.status_at,
                inner_phone=employee.user.inner_phone
            ))
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

    def find_child(self, items: List[DepartmentsModel], parent: Node):
        item: DepartmentsModel
        child = []
        for item  in items:
            if parent.id == item.parent_department_id:
                if item.is_parent:
                    node = Node( 
                        name=item.name,
                        id=item.id
                    )
                    parent.child.append(self.find_child(items ,node))
                else:
                    parent.child.append(Node(
                        name=item.name,
                        id=item.id
                    ))
        return parent