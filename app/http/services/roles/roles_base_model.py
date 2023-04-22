from pydantic import BaseModel
from typing import List
from app.http.services.access import BaseAccess

class Modules(BaseModel):
    id: int
    access: BaseAccess

class Create(BaseModel):
    name: str
    modules: List[Modules]

class Update(Create):
    id: int