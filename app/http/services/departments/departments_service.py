from app.database import DeparmentsRepository
from pydantic import BaseModel
from typing import List

class DepartmentParams(BaseModel):
    name: str
    source_department: int = None
    director_user_id: int
    deputy_head_id: List[int] = None

class Child(BaseModel):
    name:str
    id: int
    users: List[any]

class Node(BaseModel):
    name:str
    id: int
    child: List[Child]

class DeparmentResponse(BaseModel):
    nodes: Node

class DepartmentsService:

    def __init__(self, repository: DeparmentsRepository) -> None:
        self._repository: DeparmentsRepository = repository

    def get_all(self):
        
        return []
    
    def get_by_id(self, id):
        return self._repository.get_by_id()

    def add(self, params: DepartmentParams):
        return self._repository.add(params)
    
    def update(self, params: DepartmentParams, id: int):
        return self._repository.update(id, params)
    def delete(self, id):
        self._repository.delete_by_id(id)

    def create_struct(self, level_deph: int = 0):

        
    