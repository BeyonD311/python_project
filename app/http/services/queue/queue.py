import requests, json
from http.client import HTTPException
from collections.abc import Iterable
from app.http.services.logger_default import get_logger
from app.database import PositionRepository
from app.http.services.helpers import RedisInstance
from app.database.repository import Asterisk
from app.http.services.ssh import Ssh
from .queue_base_model import (
    RequestQueue, ResponseQueue , 
    ResponseQueueMembers, OuterLines, 
    RequestQueueMembers, GetAllQueue, 
    ConstField, HyperScriptParams,
    DefaultParams, User, OuterLines, IvrParams
    )

__all__ = ['QueueService']

log = get_logger("QueueService.log")

class QueueConstParams:
    """ Константные параметры из астериска """

    #для определения константных параметров
    
    _params = {}

    def _find_params(self, name:str):
        if name in self._params:
            return self._params[name]
        return None

    def __getitem__(self, name: str) -> ConstField:
        return self._find_params(name)

    def __getattr__ (self, name) -> ConstField: 
        return self._find_params(name)

    def getparams(self) -> Iterable[ConstField]:
        """ Вернет params """
        return list(self._params.values())

class StrategyParams(QueueConstParams):
    """ Параметры поля strategy """
    _params = {
        "ringall": ConstField(
            id="ringall",
            type="ringall",
            name="звонить всем",
            description="вызываются все пользователи одновременно, пока кто-нибудь не ответит"
        ),
        "leastrecent": ConstField(
            id="leastrecent",
            type="leastrecent",
            name="недавний",
            description="вызвать оператора дольше всех не принимавшего вызовы."
        ),
        "fewestcalls": ConstField(
            id="fewestcalls",
            type="fewestcalls",
            name="наименьшее количество звонков",
            description="вызвать оператора принявшего меньше всего вызовов."
        ),
        "random": ConstField(
            id="random",
            type="random",
            name="случайный",
            description="распределить вызовы случайным образом."
        ),
        "rrmemory": ConstField(
            id="rrmemory",
            type="rrmemory",
            name="по кругу",
            description="по кругу (round robin), после агента отвечавшего крайним."
        ),
        "linear": ConstField(
            id="linear",
            type="linear",
            name="по порядку",
            description="вызывать начиная с первого в порядке перечисления. Динамические агенты, будут вызываться в порядке добавления."
        ),
        "wrandom": ConstField(
            id="wrandom",
            type="wrandom",
            name="звонит случайный интерфейс",
            description="звонит случайный интерфейс, но использует штраф этого участника в качестве веса (weight) при расчете метрики."
        )
    }

class QueueService:
    def __init__(self, position_repository: PositionRepository, asterisk: Asterisk, redis: RedisInstance, hyperscript_uri: str, ssh: Ssh) -> None:
        self._repository: PositionRepository = position_repository
        self._asterisk: Asterisk = asterisk
        self._redis: RedisInstance = redis
        self.hyperscript_uri = hyperscript_uri
        self.ssh: Ssh = ssh

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
        if params.page == 0:
            params.page = 1
        queues = self._asterisk.get_all_queue(params)
        return queues

    def get_queue_members(self, uuid, fio_operators: str, fio_supervisor: str) -> ResponseQueueMembers:
        """ Получение занесенных участников очереди """
        queue_members_asterisk = set()
        if uuid is not None:
            queue_members = self._asterisk.get_queue_members(uuid)
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
        operators = [User(inner_phone=o, position=2) for o in params.operators]
        supervisors = [User(inner_phone=o, position=1) for o in params.supervisors]
        self._asterisk.add_queue_member(params=[*operators,*supervisors],name_queue=queue.name)
        self._asterisk.add_queue_phones(params=[OuterLines(name=x, is_selected=True)for x in params.numbers_lines], name_queue=queue.name)
        self._asterisk.delete_queue_members(uuid)
        self._asterisk.delete_queue_phones(uuid)
        self._asterisk.execute()
        return {
            "message": "resources add"
        }

    def add(self, params: RequestQueue):
        res = self._asterisk.add_queue(params=params)
        self._asterisk.execute()
        return {
            "message": "Create queue successful",
            "description": "Очередь успешно создана",
            "data":ResponseQueue(**res)
        }
    
    def update(self, uuid:str, params: RequestQueue):
        res = self._asterisk.update_queue(uuid, params)
        self._asterisk.execute()
        return {
            "message": "Update the queue successful",
            "description": "Обновление очереди прошло успешно",
            "data":ResponseQueue(**res)
        }

    def delete(self, uuid:str):
        self._asterisk.delete_queue(uuid)
        self._asterisk.execute()
        return {
            "message": "delete oueue",
            "description": "Очередь успешно удалена"
        }

    def get_queue_by_uuid(self, uuid: str):
        """ Получение очереди по uuid4 """
        queue = self._asterisk.get_queue_by_uuid(uuid)
        return self.__queue_filed_result(queue)
    
    async def get_default_params(self):
        strategy = StrategyParams().getparams()
        params = DefaultParams(
            strategy=strategy
        )
        del strategy
        request = requests.get(self.hyperscript_uri+"/api/forms/")
        if request.status_code != 200:
            raise HTTPException({
                "message": "hyper script fail request",
                "description": "Запрос не 200"
            })
        for hyperscript_params in request.json()['data']:
            hyperscript_params['id'] = hyperscript_params['uuid_form']
            covertParams = HyperScriptParams(**hyperscript_params)
            params.hyperscript.append(covertParams)
            
        ivrs = await self._redis.redis.get("ivrs")
        if ivrs is None:
            self.ssh.exec("ls /etc/asterisk/queue_ivrs/")
            ivrs = self.ssh.output
            await self._redis.redis.set("ivrs", json.dumps(ivrs), ex=3600)
        else:
            ivrs = json.loads(ivrs)
        ivrs = [IvrParams(id=ivr,name=ivr) for ivr in ivrs]
        params.ivrs = ivrs
        return params

    def __queue_filed_result(self, queue) -> ResponseQueue:
        """ Преобразование ответа """
        res = {
            "name_queue_operator": queue['name'],
            "type": queue['type_queue'],
            "active": queue['queue_enabled'],
            "uuid": queue['uuid'],
            "base_info": {
                "description": queue['description'],
                "exten": queue['exten'],
                "queue_code": queue['queue_code'],
                "strategy": queue['strategy'],
                "weight": queue['weight']
            },
            "config_call": {
                "timeout": queue['timeout'],
                "wrapuptime": queue['wrapuptime'],
                "timeout_talk": queue['timeout_talk'],
                "timeout_queue": queue['timeout_queue'],
                "maxlen": queue['maxlen']
            },
            "script_ivr": {
                "name": queue['script_ivr_name'],
                "hyperscript": queue['script_ivr_hyperscript'],
            }
        }
        return ResponseQueue(**res)