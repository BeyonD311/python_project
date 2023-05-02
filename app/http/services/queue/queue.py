from app.http.services.logger_default import get_logger
from app.http.services.helpers import convert_second_to_time
from app.database import PositionRepository
from app.http.services.helpers import RedisInstance
from app.database.repository import Asterisk
from .queue_base_model import (RequestQueue, ResponseQueue , ResponseQueueMembers, OuterLines, RequestQueueMembers, GetAllQueue)

__all__ = ['QueueService']

log = get_logger("QueueService.log")



class QueueService:
    def __init__(self, position_repository: PositionRepository, asterisk: Asterisk, redis: RedisInstance) -> None:
        self._repository: PositionRepository = position_repository
        self._asterisk: Asterisk = asterisk
        self._redis: RedisInstance = redis

    def get_state_queue(self, uuid):
        return self._asterisk.get_state_queue(uuid)

    def set_state(self, uuid: str, status: bool): 
        self._asterisk.set_queue_state(uuid, status)
        self._asterisk.execute()
        return {
            "message": "status add",
            "description": "Статус обновлен"
        }
    
    def get_queues(self, params: GetAllQueue):
        if params.page == 1:
            params.page = 0
        queues = self._asterisk.get_all_queue(params)
        return queues

    def get_queue_members(self, uuid, fio_operators: str, fio_supervisor: str) -> ResponseQueueMembers:
        """ Получение занесенных участников очереди """
        queue_members = self._asterisk.get_queue_members(uuid)
        queue_members_asterisk = set()
        for member in queue_members:
            queue_members_asterisk.add(member.uniqueid)
        employees = [*self._repository.get_users_by_position(2, fio_operators), *self._repository.get_users_by_position(1, fio_supervisor)]
        result = ResponseQueueMembers()
        for employee in employees:
            if employee.inner_phone in queue_members_asterisk:
                employee.is_selected = True
            if employee.position == 1:
                result.supervisors.append(employee)
            else:
                result.operators.append(employee)
        del employees
        outer_lines = self._asterisk.get_outer_lines(uuid)
        outer_lines_selected = self._asterisk.get_selected_outer_lines_queue(uuid)
        for line in outer_lines:
            out_line = OuterLines(
                name=line.id
            )
            if line.id in outer_lines_selected:
                out_line.is_selected = True
            result.numbers_lines.append(out_line)
        return result
    
    def save_queue_members(self, uuid: str , params: RequestQueueMembers):
        queue = self._asterisk.get_queue_by_uuid(uuid)
        self._asterisk.add_queue_member(params=[*params.operators,*params.supervisors],name_queue=queue.name)
        self._asterisk.add_queue_phones(params=params.numbers_lines, name_queue=queue.name)
        self._asterisk.delete_queue_members(uuid)
        self._asterisk.delete_queue_phones(uuid)
        self._asterisk.execute()
        

    def add(self, params: RequestQueue):
        res = self._asterisk.add_queue(params=params)
        self._asterisk.execute()
        return res
    
    def update(self, uuid:str, params: RequestQueue):
        res = self._asterisk.update_queue(uuid, params)
        self._asterisk.execute()
        return res

    def get_queue_by_uuid(self, uuid: str):
        """ Получение очереди по uuid4 """
        queue = self._asterisk.get_queue_by_uuid(uuid)
        res = {
            "name_queue_operator": queue.name,
            "type": queue.type_queue,
            "active": queue.queue_enabled,
            "uuid": queue.uuid,
            "base_info": {
                "base_info_name": queue.description,
                "queue_number": queue.queue_number,
                "queue_code": queue.queue_code,
                "queue_operator_select_method": queue.strategy,
                "queue_weight": queue.weight
            },
            "config_call": {
                "continue_one_dialer": convert_second_to_time(queue.timeout),
                "switch_number": queue.switch_number,
                "duration_talks": convert_second_to_time(queue.timeout_talk),
                "duration_call": convert_second_to_time(queue.timeout_queue),
                "simul_incoming_calls": queue.maxlen
            },
            "script_ivr": {
                "script_name": queue.script_ivr_name,
                "greeting": queue.script_ivr_greeting,
                "hyperscript": queue.script_ivr_hyperscript,
                "post_call": queue.script_ivr_post_call,
                "service_script": queue.script_ivr_service_script,
            }
        }
        return ResponseQueue(**res)