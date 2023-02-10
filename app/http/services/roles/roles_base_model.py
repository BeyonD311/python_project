from pydantic import BaseModel
from typing import List

class ParamsAccess(BaseModel):
    create: bool
    read: bool
    update: bool
    delete: bool

class Modules(BaseModel):
    id: int
    access: ParamsAccess

class Create(BaseModel):
    name: str
    modules: List[Modules]

class Update(Create):
    id: int