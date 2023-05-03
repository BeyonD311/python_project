from app.database.repository import InnerPhones
from app.http.services.inner_phone import RequestInnerPhone, Settings, Account, Design, Options, InnerPhone



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
        for item in items:
            accounts.append(
                Account(
                    id=item.id,
                    name=item.login,
                    userName=item.phone_number,
                    domainName=asterisk_host,
                    login=item.login,
                    password=item.password,
                    serverAddress=asterisk_host,
                    serverPort=asterisk_port,
                    register=item.is_registration
                )
            )
        return accounts
    
    def get_by_user_id(self, user_id: int):
        result = []
        for phone in self._repository.get_by_user_id(user_id):
            res = phone.__dict__
            result.append(InnerPhone(**res))
        return result

    def get_settings_by_user_id(self, user_id) -> Settings:
        settings = Settings(
                accounts=self._get_accounts(user_id=user_id),
                design=self._get_design(),
                options=self._get_options()
            )
        # Пока получение options захардкожена
        settings.options.display_name = settings.accounts[0].name
        return settings

    def add(self, params: RequestInnerPhone):
        self._repository.create_or_update(params)
    
    def update(self, params: RequestInnerPhone):
        self._repository.create_or_update(params)
    
    def delete(self, user_id:int, phones_id: list[int]):
        self._repository.delete_phone(user_id, phones_id)


__all__ = ["InnerPhoneServices"] 