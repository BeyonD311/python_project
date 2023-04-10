from .super import SuperRepository, NotFoundError
from app.database.models.inner_phone import InnerPhone
from app.database.models.users import UserModel
from uuid import uuid4
from typing import Callable
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session

class InnerPhones(SuperRepository):

    base_model = InnerPhone

    def __init__(self, 
                 session_factory: Callable[..., AbstractContextManager[Session]], 
                 session_asterisk: Callable[..., AbstractContextManager[Session]] = None
                 ) -> None:
        self.session_factory = session_factory
        self.session_asterisk = session_asterisk
        super().__init__(session_factory)

    def get_all(self):
        return super().get_all()

    def get_by_id(self, id: int):
        with self.session_factory() as session:
            query = session.query(self.base_model).filter(self.base_model.id == id).first()
            if query is None:
                raise NotFoundError("Not found item")
            return query
    
    def get_by_user_id(self, user_id: int):
        with self.session_factory() as session:
            query = session.query(self.base_model).filter(self.base_model.user_id == user_id).all()
            if query is None:
                raise NotFoundError("Not found item")
            return query

    def add(self, params):
        id_response = []
        with self.session_factory() as session:
            user = self._find_user(session=session, user_id=params.user_id)
            asterisk_phone = []
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
                    param = inner_phone_params.dict()
                    param['uuid'] = user.uuid
                    param['webrtc'] = "no"
                    param['transport'] = "transport-udp"
                    asterisk_phone.append(param)
                    check_default = True
                del inner_phone_params
                session.add(inner_phone)
                id_response
            session.commit()
        with self.session_asterisk() as session:
            value: dict
            for i, value in enumerate(asterisk_phone):
                user = self._check_user(session=session, params=value)
                if user is not None:
                    raise NotFoundError("The user exists")
                queries = self._create_insert_asterisk(value)
                for query in queries:
                    session.execute(query)
            session.commit()
    def update(self, params):
        asterisk_phone = []
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
                    param = inner_phone_params.dict()
                    param['last_id'] = inner_phone.phone_number
                    param['webrtc'] = "no"
                    param['transport'] = "transport-udp"
                    asterisk_phone.append(param)
                    check_default = True
                session.add(inner_phone)
            session.commit()
        with self.session_asterisk() as session:
            value: dict
            for i, value in enumerate(asterisk_phone):
                user = self._check_user(session=session, params=value)
                if user is None:
                    raise NotFoundError("The user not found")
                queries = self._update_asterisk(id=param['last_id'], params=value)
                for query in queries:
                    session.execute(query)
            session.commit()
    
    def delete_phone(self,user_id: int, phones_id: list):
        phone_number = []
        with self.session_factory() as session:
            phones = session.query(self.base_model).filter(self.base_model.id.in_(phones_id), self.base_model.user_id == user_id).all()
            for phone in phones:
                if phone.is_default:
                    phone_number.append(f"{phone.phone_number}")
                session.delete(phone)
                session.commit()
        with self.session_asterisk() as session:
            if phone_number != []:
                queries = self._delete_asterisk(",".join(phone_number))
                for query in queries:
                    session.execute(query)
            session.commit()
    def _create_insert_asterisk(self, params, w = ""):

        aors = f" insert into ps_aors(id, max_contacts) values({params['phone_number']}{w}, 1) "
        auth = f" insert into ps_auths(id, password, username, uuid,duration_call,duration_conversation) "\
               f" values({params['phone_number']}{w},'{params['password']}','{params['login']}','{params['uuid']}', '{str(params['duration_call'])}', '{str(params['duration_conversation'])}') "
        endpoints = f" insert into ps_endpoints (id, aors, auth, webrtc, transport) values ({params['phone_number']}{w}, {params['phone_number']}{w}, {params['phone_number']}{w}, '{params['webrtc']}', '{params['transport']}') "
        return aors, auth, endpoints
    
    def _check_user(self, params, session: Session):
        login = params["login"]
        sql = f" select id from ps_auths where username = '{login}' "
        return  session.execute(sql).first()
    
    def _update_asterisk(self, id, params,  w = ""):
        aors = f" update ps_aors set id = {params['phone_number']}{w} where id = {id} "
        auth = f" update ps_auths set id = {params['phone_number']}{w} , password = '{params['password']}', username = '{params['login']}', "\
               f" duration_call = '{str(params['duration_call'])}',duration_conversation = '{str(params['duration_conversation'])}' "\
               f" where id = {id} "
        endpoints = f" update ps_endpoints set id = {params['phone_number']}{w}, aors = {params['phone_number']}{w}, auth = {params['phone_number']}{w}, transport = 'transport-udp' "\
                    f" where id ={id}"
        return aors, auth, endpoints
    
    def _delete_asterisk(self, id):
        aors = f" delete from ps_aors where id in ({id})"
        auth = f" delete from ps_auths where id in ({id})"
        endpoints = f" delete from ps_endpoints where id in ({id})"
        return aors, auth, endpoints
    
    def _find_user(self, session: Session, user_id: int):
        user = session.query(UserModel).filter(UserModel.id == user_id, UserModel.is_active == True).first()
        if user is None:
            raise NotFoundError("User not found")
        return user