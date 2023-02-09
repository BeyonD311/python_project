from pydantic import BaseModel

class Access(BaseModel):
    """ 
        По типу
        CRUD
        0000 
    """
    create: bool
    read: bool
    update: bool
    delete: bool
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