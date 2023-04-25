from typing import Callable
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .super import NotFoundError

__all__ = ["Asterisk", "AsteriskParams", "ExceptionAsterisk", "StatusHistoryParams"]

class AsteriskParams(BaseModel):
    phone_number: str
    password: str
    login: str
    uuid: str
    duration_call: float
    duration_conversation: float
    webrtc: str
    transport: str

class StatusHistoryParams(BaseModel):
    time_at: int
    user_uuid: str
    user_c: str
    source: str
    destination: str
    code: str
    call_time: str = None

class Asterisk():
    """ 
        Для работы с таблицами астера
    """
    def __init__(self, session_asterisk: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_asterisk = session_asterisk
        self.stack_multiple_query = []
    def insert_sip_user_asterisk(self, params: AsteriskParams, w = ""):
        """ 
            Создание номера в asterisk(sip регистрация)
        """
        aors = f" insert into ps_aors(id, max_contacts) values({params.phone_number}{w}, 1) "
        auth = f" insert into ps_auths(id, password, username, uuid,duration_call,duration_conversation, status) "\
               f" values({params.phone_number}{w},'{params.password}','{params.login}','{params.uuid}', '{params.duration_call}',"\
                f" '{params.duration_conversation}', 10)"
        endpoints = f" insert into ps_endpoints (id, aors, auth, webrtc, transport) values "\
                f"({params.phone_number}{w}, {params.phone_number}{w}, {params.phone_number}{w}, '{params.webrtc}', '{params.transport}') "
        self.stack_multiple_query.append(aors)
        self.stack_multiple_query.append(auth)
        self.stack_multiple_query.append(endpoints)
    
    def get_by_user_login(self, username: str):
        with self.session_asterisk() as session:
            query = session.execute(f" select id from ps_auths where username = '{username}' ").first()
            session.close()
            return  query

    def get_by_user_phone(self, phone: str):
        with self.session_asterisk() as session:
            query = session.execute(f" select id from ps_auths where id = '{phone}' ").first()
            session.close()
            return  query

    def update_sip_user_asterisk(self, id, params: AsteriskParams,  w = ""):
        aors = f" update ps_aors set id = {params.phone_number}{w} where id = {id} "
        auth = f" update ps_auths set id = {params.phone_number}{w} , password = '{params.password}', username = '{params.login}', "\
               f" duration_call = '{params.duration_call}',duration_conversation = '{params.duration_conversation}' "\
               f" where id = {id} "
        endpoints = f" update ps_endpoints set id = {params.phone_number}{w}, aors = {params.phone_number}{w}, auth = {params.phone_number}{w}, transport = 'transport-udp' "\
                    f" where id ={id}"
        self.stack_multiple_query.append(aors)
        self.stack_multiple_query.append(auth)
        self.stack_multiple_query.append(endpoints)

    def delete_sip_user_asterisk(self, id):
        aors = f" delete from ps_aors where id in ({id})"
        auth = f" delete from ps_auths where id in ({id})"
        endpoints = f" delete from ps_endpoints where id in ({id})"
        self.stack_multiple_query.append(aors)
        self.stack_multiple_query.append(auth)
        self.stack_multiple_query.append(endpoints)
    
    def save_sip_status_asterisk(self, status_id, uuid):
        query = f" update ps_auths set status = {status_id} where ps_auths.uuid = \"{uuid}\" "
        self.stack_multiple_query.append(query)
    
    def check_device_status(self, uuid) -> bool:
        '''
            Фукция для проверки статуса оборудования (если offline или None == false) true
        '''
        with self.session_asterisk() as session:
            query = session.execute(f"select device_state from ps_auths where ps_auths.uuid = \"{uuid}\"").first()
            flag = False
            if query is not None and query[0] == "online": 
                flag = True
            session.close()
            return flag
    
    def get_phones_by_user_uuid(self, uuid:str ):
        with self.session_asterisk() as session:
            query = session.execute(f"select id from ps_auths where uuid='{uuid}'").all()
            session.commit()
            return query


    def set_status_history(self, params: StatusHistoryParams):
        self.stack_multiple_query.append(f"CALL AddStatusHistory({params.time_at}, '{params.user_uuid}', '{params.user_c}', '{params.source}', '{params.destination}', '{params.code}', NULL)")
        
    def execute(self):
        session: Session
        with self.session_asterisk() as session:
            while self.stack_multiple_query != []:
                query = self.stack_multiple_query.pop()
                session.execute(query)
            session.commit()

class ExceptionAsterisk(NotFoundError):
    entity_name: str
    def __init__(self, message):
        super().__init__(f"{message}")