from pydantic import BaseModel

class BaseAccess(BaseModel):
    """ 
        По типу
        CRUD
        0000 
    """
    create: bool = False
    read: bool = False
    update: bool = False
    delete: bool = False

class Access(BaseAccess):
    map: dict

    def __str__(self):
        self.create = int(self.create)
        self.read = int(self.read)
        self.update = int(self.update) 
        self.delete = int(self.delete)
        return f"{self.create}{self.read}{self.update}{self.delete}"
    

def parse_access(str_model: str) -> Access:
    modules = [*str_model]
    for i in range(len(modules)):
        modules[i] = bool(int(modules[i]))
    return Access(
        create=modules[0],
        read=modules[1],
        update=modules[2],
        delete=modules[3],
        map={
            "get": modules[1],
            "post": modules[0],
            "put": modules[2],
            "patch": modules[2],
            "delete": modules[3]
        }
    )