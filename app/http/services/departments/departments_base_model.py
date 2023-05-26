from pydantic import (BaseModel,validator)
from typing import List

__all__ = ["DepartmentParams", "Filter", "Status", "DepartmentFilter", "PositionFilter", "FilterParams"]

class DepartmentParams(BaseModel):
    name: str
    source_department: int = None
    director_user_id: int = None
    deputy_head_id: List[int] = None

class Node(BaseModel):
    name:str
    id: int
    child: List = []

class BaseFilter(BaseModel):
    id: int
    name: str

class Status(BaseFilter):
    pass
class DepartmentFilter(BaseFilter):
    pass
class PositionFilter(BaseFilter):
    pass

class FilterParams(BaseModel):
    statuses:list[Status]
    departments: list[DepartmentFilter]
    positions: list[PositionFilter]

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