from app.database import EmployeesRepository, DeparmentsRepository
from pydantic import BaseModel
from typing import List
from datetime import datetime

class Employee(BaseModel):
    name: str
    department_id: int = None
    director_user_id: int
    deputy_head_id: List[int] = None


class EmployeeResponse(BaseModel):
    id: int
    fio: str
    is_head_of_depatment: bool
    status: str = None
    status_at: datetime = None
    inner_phone: int = None

class EmployeesService:
    def __init__(self, employees_repository: EmployeesRepository) -> None:
        self._repository: EmployeesRepository = employees_repository
    
    def add(self, params: Employee):
        
        self._repository.add(params)