from pydantic import BaseModel

class BaseAccess(BaseModel):
    """
        По типу
        create: 0
        read: 0
        update: 0
        delete: 0
        Пятый ноль пудет отвечать за доступ только для текущего пользователя 
        
        00000
    """
    create: bool = False
    read: bool = False
    update: bool = False
    delete: bool = False
    personal: bool = False

class Access():
    def __init__(self, method: str = "empty", str_model: str = None) -> None:
        self._base_access: BaseAccess = None
        self._method = method.lower()
        self._access_map = None
        if str_model is not None:
            self._parse_access(str_model=str_model)

    def __str__(self):
        return f"{int(self.create)}{int(self.read)}{int(self.update)}{int(self.delete)}{int(self.user)}"
    
    def parse(self, str_model: str):
        self._parse_access(str_model=str_model)
        return self
    
    def check_access_method(self) -> bool:
        if self._method not in self._access_map:
            return False
        return self._access_map[self._method]
    
    def get_access_model(self) -> BaseAccess:
        return self._base_access
    
    def check_personal(self) -> bool:
        return self._base_access.current_user
    
    """ Парсинг  """
    def _parse_access(self,str_model: str) -> None:
        modules = [*str_model]
        for i in range(len(modules)):
            modules[i] = bool(int(modules[i]))
        self._base_access = BaseAccess(
            create = modules[0],
            read=modules[1],
            update=modules[2],
            delete=modules[3],
            personal=modules[4]
        )
        self._access_map={
            "get": modules[1],
            "post": modules[0],
            "put": modules[2],
            "patch": modules[2],
            "delete": modules[3]
        }
    
    
