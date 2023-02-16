from app.database import DeparmentsRepository, DepartmentsModel
from pydantic import BaseModel
from typing import List, Iterator

class DepartmentParams(BaseModel):
    name: str
    source_department: int = None
    director_user_id: int
    deputy_head_id: List[int] = None

class Node(BaseModel):
    name:str
    id: int
    child: List = []
    employees: List = []

class DeparmentResponse(BaseModel):
    nodes: Node

class DepartmentsService:

    def __init__(self, repository: DeparmentsRepository) -> None:
        self._repository: DeparmentsRepository = repository

    def get_all(self):
        items = self._repository.get_all()
        res = []
        for item in items:
            if item.parent_department_id != None:
                continue
            node = Node(
                    name=item.name,
                    id=item.id,
                    employees=item.employees
                )
            if item.is_parent:
                self.find_child(items, node)
            res.append(node)
        return res
    
    def get_by_id(self, id):
        return self._repository.get_by_id()

    def add(self, params: DepartmentParams):
        return self._repository.add(params)
    
    def update(self, params: DepartmentParams, id: int):
        return self._repository.update(id, params)
    def delete(self, id):
        self._repository.delete_by_id(id)

    def find_child(self, items: List[DepartmentsModel], parent: Node):
        item: DepartmentsModel
        child = []
        for i, item  in enumerate(items):
            if parent.id == item.parent_department_id:
                if item.is_parent:
                    node = Node( 
                        name=item.name,
                        id=item.id,
                        employees=item.employees
                    )
                    parent.child.append(self.find_child(items ,node))
                else:
                    parent.child.append(Node(
                        name=item.name,
                        id=item.id,
                        employees=item.employees,
                        child=child
                    ))
        return parent