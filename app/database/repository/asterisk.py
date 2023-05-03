from typing import Callable
from math import ceil
from uuid import uuid4
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .super import NotFoundError, Pagination

from app.http.services.helpers import convert_time_to_second

__all__ = ["Asterisk", "AsteriskParams", "ExceptionAsterisk", "StatusHistoryParams"]


# Параметры для фильтрации выборки
queueFilter = {
    "NAME": lambda n: "and LOWER(name) like '%"+n+"%'",
    "STATUS": lambda status: "and status in (" + status + ")",
    "TYPE": lambda type: "and LOWER(type) = '" + str(type).lower() + "'"
}
    

class AsteriskParams(BaseModel):
    phone_number: str
    password: str
    login: str
    uuid: str
    duration_call: float
    duration_conversation: float
    webrtc: str
    transport: str

class QueueMembers(BaseModel):
    membername: int
    uuid_queue: str
    uniqueid: int

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
        aors =  f" insert into ps_aors(id, max_contacts) values({params.phone_number}{w}, 1) "
        auth =  f" insert into ps_auths(id, password, username, uuid,duration_call,duration_conversation, status) "\
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
    
    def get_outer_lines(self, uuid: str):
        """ Получение всех внешних линий """
        with self.session_asterisk() as session:
            sql = "select id from ps_auths where uuid is null "\
                    "and id not in ( "\
                    "select SUBSTRING_INDEX(phone, '/', -1) phone from queues q "\
                    "join queue_phones qp on qp.queue_name = q.name "
            if uuid is not None:    
                sql = sql + f" where uuid != '{uuid}' "
            sql = sql + " )"
            print(sql)
            query = session.execute(sql).all()
            session.close()
            return query

    def get_selected_outer_lines_queue(self, uuid: str) -> set:
        """ Получение внешних линий у выбранной очереди """
        with self.session_asterisk() as session:
            query = session.execute(f"select qp.phone from queues q join queue_phones qp on qp.queue_name = q.name where q.uuid = '{uuid}'").all()
            session.close()
            res = set()
            for select_out_line in query:
                split = select_out_line.phone.split("/")
                res.add(split[1])
            return res
    
    def get_queue_members(self, uuid):
        with self.session_asterisk() as session:
            sql = "select qm.uniqueid, qm.membername, q.uuid from queues q "\
                  "left join queue_members qm on qm.queue_name = q.name "\
                  f"where q.uuid = '{uuid}'"
            query = session.execute(sql).all()
            session.close()
            return query
    
    def delete_queue_members(self, uuid):
        query = "delete from queue_members "\
                f"where queue_name = (select name from queues q where uuid = '{uuid}');"
        self.stack_multiple_query.append(query)
    
    def delete_queue_phones(self, uuid):
        query = "delete from queue_phones "\
                f"where queue_name = ( select name from queues q where uuid = '{uuid}');"
        self.stack_multiple_query.append(query)

    def get_all_queue(self, params):
        """ Получениые всех очередей """
        select_queue = "select q.uuid as `uuid`, name, queue_enabled as status, type_queue as type, count(qm.member_position) as operators"\
                        " from queues q"\
                        " left join queue_members qm on qm.queue_name = q.name and qm.member_position = 2"\
                        f" GROUP by q.name HAVING 1=1"
        select_queue = select_queue + " " + self.__filter_queues(params.filter)
        select_queue_limit = select_queue + f" limit {params.page * params.size}, {params.size}"
        select_wrapper = f"select * from ({select_queue_limit}) temp_queue "
        select_wrapper = select_wrapper + " " + self.__order_by_queues(params.order_field, params.order_direction)
        if params.page == 0:
            params.page = 1
        with self.session_asterisk() as session:
            query = session.execute(select_wrapper).all()
            total = self.__total(session=session, select_queue=select_queue)
            session.close()
            total_page=ceil(total / params.size)
            return {
                "data": query,
                "pagination": Pagination(
                    page=params.page,
                    total_page=total_page,
                    size=params.size,
                    total_count=total,
                )
            }
    
    def get_state_queue(self, uuid):
        with self.session_asterisk() as session:
            sql = "select q.uuid as `uuid`, queue_enabled as status, "\
                "sum(if(qm.member_position = 2, 1, 0)) as operators, sum(if(qm.member_position = 1, 1, 0)) as supervisors "\
                f"from queues q left join queue_members qm on qm.queue_name = q.name where uuid = '{uuid}'"
            state_queue = session.execute(sql).first()
            if state_queue is None:
                raise NotFoundError()
            session.close()
            return state_queue

    def __total(self, session: Session, select_queue):
        total = session.execute(f"select count(*) as `count` from ({select_queue}) temp_c").first()
        if total is None:
            return 1
        return total.count
    def __order_by_queues(self, field: str, value: str) -> str:
        """ Получение сортировки """
        res = ""
        available_fields = ["name", "status", "type", "operators"]
        if field.lower() in available_fields:
            res = 'order by `' + field.lower() + '`' + " "
            if value.lower() == "asc":
                res = res + "asc"
            else:
                res = res + "desc"
        return res

    def __filter_queues(self, params: list) -> str:
        res = ""
        for filter in params:
            try:
                action = queueFilter[filter.field]
                res = res + " " + action(filter.value)
            except Exception:
                continue
        return res

    def set_queue_state(self, uuid: str, status: bool):
        sql = f"update queues set queue_enabled = {status} where uuid = '{uuid}'"
        self.stack_multiple_query.append(sql)
    
    def add_queue_member(self, params, name_queue):
        for param in params:
            query = "insert into asterisk.queue_members"\
                    "(queue_name, interface, membername, state_interface, penalty, paused, uniqueid, ringinuse, member_position) "\
                    f"values('{name_queue}', 'Local/{param.inner_phone}@operators_calls', '{param.inner_phone}', 'PJSIP/{param.inner_phone}', 1, 0,'{param.inner_phone}', 'no', {param.position});"
            self.stack_multiple_query.append(query)

    def add_queue_phones(self, params, name_queue):
        for param in params:
            query = f"insert into queue_phones(phone, queue_name) values('PJSIP/{param.name}','{name_queue}')"
            self.stack_multiple_query.append(query)

    def add_queue(self, params):
        """ Добавление новых очередей """
        queue_fields = self.__params_queue_fields()
        queue_fields_values = self.__value_fields_queues(params)
        uuid = uuid4()
        base = ",".join(queue_fields_values['values_base'])
        base_info = ",".join(queue_fields_values['values_base_info'])
        value_calls = ",".join(queue_fields_values['values_config_calls'])
        script_value = ",".join(queue_fields_values['values_script_ivr'])

        query = f"insert into queues({queue_fields['base']}, {queue_fields['base_info']}, {queue_fields['config_calls']}, {queue_fields['script_ivr']}, `uuid`) "\
            f"values({base}, {base_info}, {value_calls}, {script_value}, '{uuid}');"
        self.stack_multiple_query.append(query)
        res = params.dict()
        res['uuid'] = str(uuid)
        return res
    
    def update_queue(self, uuid, params):
        queue_fields = self.__params_queue_fields()
        queue_fields_values = self.__value_fields_queues(params)
        update = []
        for field, value in queue_fields_values.items():
            field = field.replace("values_", "")
            set_fields = queue_fields[field].split(",")
            for key, queue_field in enumerate(set_fields):
                update.append(f"{queue_field} = {value[key]}")
        update = ",".join(update)
        self.stack_multiple_query.append(f"update queues set {update} where uuid = '{uuid}'")
        res = params.dict()
        res['uuid'] = str(uuid)
        return res


    def get_queue_by_uuid(self, uuid: str):
        queue_fields = self.__params_queue_fields()
        query = f"select {queue_fields['base']}, {queue_fields['base_info']}, {queue_fields['config_calls']}, {queue_fields['script_ivr']}, `uuid` from queues "\
                f"where `uuid` = '{uuid}' "
        with self.session_asterisk() as session:
            query = session.execute(query).first()
            if query == None:
                raise ExceptionAsterisk("Queue not found")
            session.close()
            return query
    
    def __params_queue_fields(self) -> dict:
        """ Параметры таблицы queues для (GET, POST, UPDATE) """
        return {
            "base": "`name`,  `type_queue`, `queue_enabled` ",
            "base_info": "`description`, `queue_code`, `exten`, `strategy`, `weight` ",
            "config_calls": "`timeout`, `wrapuptime`, `timeout_talk`, `timeout_queue`, `maxlen` ",
            "script_ivr": "`script_ivr_name`, `script_ivr_hyperscript` ",
        }

    def __value_fields_queues(self, params)->dict:
        """ Значения полей из параметров 
            заносим значение согласно полям в методе __params_queue_fields
            Для update будет собираться автоматически
        """
        return {
            "values_base": [f"'{params.name}'", f"'{params.type_queue}'", f"{params.queue_enabled}"],
            "values_base_info": [
                f"'{params.base_info.description}'",
                f"{params.base_info.queue_code}", 
                f"{params.base_info.exten}",
                f"'{params.base_info.strategy}'",
                f"{params.base_info.weight}"
            ],
            "values_config_calls": [
                f"{convert_time_to_second(params.config_call.timeout)}",
                f"{convert_time_to_second(params.config_call.wrapuptime)}",
                f"{convert_time_to_second(params.config_call.timeout_talk)}",
                f"{convert_time_to_second(params.config_call.timeout_queue)}",
                f"{params.config_call.maxlen}"
            ],
            "values_script_ivr": [
                f"'{params.script_ivr.name}'",
                f"'{params.script_ivr.hyperscript}'"
            ]
        }

    def set_status_history(self, params: StatusHistoryParams):
        """ Добовление истории статусов """
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