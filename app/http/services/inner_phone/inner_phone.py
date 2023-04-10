from app.database.repository import InnerPhones, NotFoundError
from app.database.models import InnerPhone
from app.http.services.inner_phone import InnerPhone, RequestInnerPhone

class InnerPhoneServices:
    
    def __init__(self, inner_phone_repository: InnerPhones) -> None:
        self._repository: InnerPhones = inner_phone_repository
    
    def get_by_id(self, id: int):
        result = []
        for phone in self._repository.get_by_user_id(id):
            res = phone.dict()
            del res['uuid']
            result.append(phone)
        return result

    def get_by_user_id(self, user_id):
        return self._repository.get_by_user_id(user_id)
    
    def add(self, params: RequestInnerPhone):
        self._repository.add(params)
    
    def update(self, params: RequestInnerPhone):
        self._repository.update(params)
    
    def delete(self, user_id:int, phones_id: list[int]):
        self._repository.delete_phone(user_id, phones_id)

__all__ = ["InnerPhoneServices"] 