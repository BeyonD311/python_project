from app.database.repository import InnerPhones, NotFoundError
from app.database.models import InnerPhone
from app.http.services.inner_phone import InnerPhone, RequestInnerPhone, Settings, Account, Design, Options

class InnerPhoneServices:
    
    def __init__(self, inner_phone_repository: InnerPhones) -> None:
        self._repository: InnerPhones = inner_phone_repository

    @staticmethod
    def _get_design() -> Design:
        design = Design()
        return design

    @staticmethod
    def _get_options() -> Options:
        options = Options()
        return options

    def _get_accounts(self, user_id) -> list[Account]:
        accounts = []
        items = self.get_by_user_id(user_id=user_id)
        asterisk_host = self._repository.get_asterisk_host()
        asterisk_port = self._repository.get_asterisk_port()
        print(items)
        for item in items:
            accounts.append(
                Account(
                    id=item.uuid,
                    name=item.login,
                    userName=item.login,
                    domainName=asterisk_host,
                    login=item.login,
                    password=item.password,
                    serverAddress=asterisk_host,
                    serverPort=asterisk_port,
                    register=item.is_registration
                )
            )
        return accounts

    def get_by_id(self, id: int):
        result = []
        for phone in self._repository.get_by_user_id(id):
            res = phone.dict()
            del res['uuid']
            result.append(phone)
        return result

    def get_by_user_id(self, user_id: int):
        return self._repository.get_by_user_id(user_id)

    def get_settings_by_user_id(self, user_id) -> Settings:
        settings = Settings(
                accounts=self._get_accounts(user_id=user_id),
                design=self._get_design(),
                option=self._get_options()
            )
        # Пока получение options захардкожена
        settings.option.display_name = settings.accounts[0].name
        return settings

    def add(self, params: RequestInnerPhone):
        self._repository.add(params)
    
    def update(self, params: RequestInnerPhone):
        self._repository.update(params)
    
    def delete(self, user_id:int, phones_id: list[int]):
        self._repository.delete_phone(user_id, phones_id)


__all__ = ["InnerPhoneServices"] 