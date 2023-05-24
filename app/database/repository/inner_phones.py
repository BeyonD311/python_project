from .super import SuperRepository, NotFoundError, ExistsException
from app.database.models.inner_phone import InnerPhone
from app.database.models.users import UserModel
from uuid import uuid4
from typing import Callable
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from .asterisk import Asterisk, AsteriskParams
from re import search
from sqlalchemy.exc import IntegrityError

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
                description = f"Не найден внутренний номер с ID={id}."
                raise NotFoundError(entity_id=id, entity_description=description)
            return query

    def add(self, arg):
        pass

    def update(self):
        pass

    def get_by_user_id(self, user_id: int):
        """ Для получения всех телефонов по id если """
        # TODO добавить issues для исправления(убрать исключение на уровне запроса)
        with self.session_factory() as session:
            query = session.query(self.base_model).filter(self.base_model.user_id == user_id).all()
            if not query:
                description = f"У пользователя не обнаруженны номера с ID={user_id}."
                raise NotFoundError(entity_id=user_id, entity_description=description)
            return query

    def get_by_user_id_all(self, user_id: int):
        """ Для получения всех телефонов по id если нет то пустой массив """
        with self.session_factory() as session:
            query = session.query(self.base_model).filter(self.base_model.user_id == user_id).all()
            result = []
            for phone in query:
                phone.users
                result.append(phone)
            return result

    def create_or_update(self, params) -> list:
        count_default = 0
        response = []
        with self.session_factory() as session:
            user = self.__find_user(session=session, user_id=params.user_id)
            phones = session.query(self.base_model).filter(self.base_model.user_id == user.id).all()
            phones_asterisk = []
            phone: InnerPhone
            for phone in phones:
                if phone.is_default:
                    pattern = r'[^0-9\s]*'
                    if search(pattern=pattern, string=str(phone.phone_number)) is None:
                        phones_asterisk.append(str(phone.phone_number))
                session.delete(phone)
            session.commit()
            phones = self.session_asterisk.get_phones_by_user_uuid(user.uuid)
            for phone in phones:
                phones_asterisk.append(str(phone.id))
            if len(phones_asterisk) > 0:
                self.session_asterisk.delete_sip_user_asterisk(",".join(phones_asterisk))
                self.session_asterisk.execute()
            for inner_phone in params.inner_phones:
                phone = InnerPhone(
                    uuid = uuid4(),
                    user_id = user.id,
                    phone_number = inner_phone.phone_number,
                    description = inner_phone.description,
                    is_registration = inner_phone.is_registration,
                    is_default = inner_phone.is_default,
                    login = inner_phone.login,
                    password = inner_phone.password,
                    duration_call = inner_phone.duration_call,
                    duration_conversation = inner_phone.duration_conversation,
                    incoming_calls = inner_phone.incoming_calls,
                    comment = inner_phone.comment
                )
                if inner_phone.id > 0:
                    phone.id = inner_phone.id
                if inner_phone.is_registration and inner_phone.is_default and count_default == 0:
                    check_phone = self.session_asterisk.get_by_user_phone(inner_phone.phone_number)
                    if check_phone is not None:
                        description = f"Уже существует номер: {inner_phone.phone_number}"
                        raise ExistsException(item=inner_phone.phone_number, entity_description=description)
                    param = self.__params(user, phone, inner_phone)
                    self.session_asterisk.insert_sip_user_asterisk(param)
                    count_default += 1
                session.add(phone)
            # TODO: номер добавляется при наличии такого же
            # TODO: "is_registration": true/false -> удаляет запись
            # TODO: "is_default": true/false -> удаляет запись
            session.commit()
            try:
                self.session_asterisk.execute()
            except IntegrityError:
                description = f"Уже существует номер: {inner_phone.phone_number}"
                raise ExistsException(item=inner_phone.phone_number, entity_description=description)
        return response

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
            self.session_asterisk.delete_sip_user_asterisk(",".join(phone_number))
            self.session_asterisk.execute()

    def __find_user(self, session: Session, user_id: int):
        user = session.query(UserModel).filter(UserModel.id == user_id, UserModel.is_active == True).first()
        if user is None:
            description = f"Не найден пользователь с ID={user_id}."
            raise NotFoundError(entity_id=user_id, entity_description=description)
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

    def get_phone_by_id(self, user_id: int):
        with self.session_factory() as session:
            phone = session.query(self.base_model.phone_number).filter(self.base_model.user_id == user_id).first()
            if not phone:
                return None
            return phone[0]


class PhoneFoundError(NotFoundError):
    def __init__(self, message):
        super().__init__(f"{message}")