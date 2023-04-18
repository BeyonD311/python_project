from .super import SuperRepository, NotFoundError
from pydantic import BaseModel
from app.database.models.inner_phone import InnerPhone
from app.database.models.users import UserModel
from uuid import uuid4
from typing import Callable
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from .asterisk import Asterisk, AsteriskParams

class InnerPhones(SuperRepository):

    base_model = InnerPhone

    def __init__(self, 
                 session_factory: Callable[..., AbstractContextManager[Session]], 
                 session_asterisk: Callable[..., AbstractContextManager[Session]] = None,
                 asterisk_host: Callable[..., AbstractContextManager[Session]] = None,
                 asterisk_port: Callable[..., AbstractContextManager[Session]] = None,
                 ) -> None:
        self.session_factory = session_factory
        self.session_asterisk: Asterisk = Asterisk(session_asterisk)
        self.asterisk_host = asterisk_host
        self.asterisk_port = asterisk_port
        super().__init__(session_factory)

    def get_all(self):
        return super().get_all()

    def get_asterisk_host(self):
        return self.asterisk_host

    def get_asterisk_port(self):
        return self.asterisk_port

    def get_by_id(self, id: int):
        with self.session_factory() as session:
            query = session.query(self.base_model).filter(self.base_model.id == id).first()
            if not query:
                raise NotFoundError("Not found item")
            return query
    
    def get_by_user_id(self, user_id: int):
        with self.session_factory() as session:
            query = session.query(self.base_model).filter(self.base_model.user_id == user_id).all()
            if not query:
                raise NotFoundError("Not found item")
            return query
        
    def create_or_update(self, params) -> list:
        count_default = 0
        response = []
        with self.session_factory() as session:
            user = self.__find_user(session=session, user_id=params.user_id)
            phones = session.query(self.base_model).filter(self.base_model.user_id == user.id).all()
            phones_asterisk = []
            phone: InnerPhone
            for phone in phones:
                phones_asterisk.append(phone.phone_number)
                session.delete(phone)
            if phones_asterisk != []:
                self.session_asterisk.delete_asterisk(",".join)
            for inner_phone in params.inner_phones:
                phone = InnerPhone(
                    uuid = uuid4(),
                    user_id = user.id,
                    phone_number = inner_phone.phone_number,
                    description = inner_phone.description,
                    is_registration = inner_phone.registration,
                    is_default = inner_phone.default,
                    login = inner_phone.login,
                    password = inner_phone.password,
                    duration_call = inner_phone.duration_call,
                    duration_conversation = inner_phone.duration_conversation,
                    incoming_calls = inner_phone.incoming_calls,
                    comment = inner_phone.comment
                )
                if inner_phone.registration and inner_phone.default and count_default == 0:
                    check_phone = self.session_asterisk.get_by_user_phone(inner_phone.phone_number)
                    if check_phone is not None:
                        raise PhoneFoundError(f"Телефон уже существует {inner_phone.phone_number}")
                    param = self.__params(user, phone, inner_phone)
                    self.session_asterisk.create_insert_asterisk(param)
                    count_default += 1
                response.append(inner_phone)
                session.add(inner_phone)
            session.commit()
            self.session_asterisk.execute()
        return response
            

    def add(self, params):

        with self.session_factory() as session:
            user = self.__find_user(session=session, user_id=params.user_id)
            check_default = False
            for inner_phone_params in params.inner_phones:
                inner_phone = InnerPhone(
                    uuid = uuid4(),
                    user_id = user.id,
                    phone_number = inner_phone_params.phone_number,
                    description = inner_phone_params.description,
                    is_registration = inner_phone_params.registration,
                    is_default = inner_phone_params.default,
                    login = inner_phone_params.login,
                    password = inner_phone_params.password,
                    duration_call = inner_phone_params.duration_call,
                    duration_conversation = inner_phone_params.duration_conversation,
                    incoming_calls = inner_phone_params.incoming_calls,
                    comment = inner_phone_params.comment
                )
                if inner_phone_params.registration and inner_phone_params.default and check_default == False:
                    check_phone = self.session_asterisk.get_by_user_phone(inner_phone_params.phone_number)
                    if check_phone is not None:
                        raise ExceptionAsterisk("Пользователь с таким номером уже зарегистрирован")
                    param = self.__params(user,inner_phone, inner_phone_params)
                    self.session_asterisk.create_insert_asterisk(param)
                    check_default = True
                del inner_phone_params
                session.add(inner_phone)
            session.commit()
            self.session_asterisk.execute()
    def update(self, params):
        check_default = False
        with self.session_factory() as session:
            user = self._find_user(session=session, user_id=params.user_id)
            for inner_phone_params in params.inner_phones:
                inner_phone = session.query(self.base_model).filter(self.base_model.id == inner_phone_params.id).first()
                if inner_phone is None:
                    continue
                inner_phone.description = inner_phone_params.description,
                inner_phone.is_registration = inner_phone_params.registration,
                inner_phone.is_default = inner_phone_params.default,
                inner_phone.login = inner_phone_params.login,
                inner_phone.password = inner_phone_params.password,
                inner_phone.duration_call = inner_phone_params.duration_call,
                inner_phone.duration_conversation = inner_phone_params.duration_conversation,
                inner_phone.incoming_calls = inner_phone_params.incoming_calls,
                inner_phone.comment = inner_phone_params.comment
                if inner_phone_params.registration and inner_phone_params.default and check_default == False:
                    check_phone = self.session_asterisk.get_by_user_phone(inner_phone_params.phone_number)
                    if check_phone is not None:
                        raise Not
                    param = self.__params(user,inner_phone, inner_phone_params)
                    self.session_asterisk.create_insert_asterisk(param)
                    check_default = True
                del inner_phone_params
                session.add(inner_phone)
            session.commit()
            self.session_asterisk.execute()
    
    def delete_phone(self,user_id: int, phones_id: list):
        phone_number = []
        with self.session_factory() as session:
            phones = session.query(self.base_model).filter(self.base_model.id.in_(phones_id), self.base_model.user_id == user_id).all()
            for phone in phones:
                if phone.is_default:
                    phone_number.append(f"{phone.phone_number}")
                session.delete(phone)
                session.commit()
        if phone_number != []:
            self.session_asterisk.delete_asterisk(",".join(phone_number))
            self.session_asterisk.execute
    
    def __find_user(self, session: Session, user_id: int):
        user = session.query(UserModel).filter(UserModel.id == user_id, UserModel.is_active == True).first()
        if user is None:
            raise NotFoundError("User not found")
        return user
    
    def __params(self, user: UserModel, inner_phone: InnerPhone, inner_phone_params) -> AsteriskParams:
        asterisk_params = AsteriskParams(
            phone_number=inner_phone.phone_number,
            uuid=user.uuid,
            webrtc="yes",
            transport="transport-wss",
            login=inner_phone_params.login,
            password=inner_phone_params.password,
            duration_call= (inner_phone_params.duration_call.hour * 3600) + (inner_phone_params.duration_call.minute * 60) + inner_phone_params.duration_call.second,
            duration_conversation = (inner_phone_params.duration_conversation.hour * 3600) \
            + (inner_phone_params.duration_conversation.minute * 60) \
            + inner_phone_params.duration_conversation.second,
        )
        return asterisk_params

class PhoneFoundError(NotFoundError):
    def __init__(self, message):
        super().__init__(f"{message}")