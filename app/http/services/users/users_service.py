import datetime, json, asyncio
from fastapi.websockets import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK
from aioredis.client import PubSub
from hashlib import sha256
from app.http.services.logger_default import get_logger
from app.database import UserModel
from app.database import UserRepository
from app.database import NotFoundError, UserNotFoundError
from app.database import SkillsRepository
from app.http.services.helpers import RedisInstance, convert_second_to_time
from app.http.services.users.user_base_models import UsersResponse
from app.http.services.users.user_base_models import ResponseList
from app.http.services.users.user_base_models import UserRequest
from app.http.services.users.user_base_models import UserParams
from app.http.services.users.user_base_models import UserDetailResponse
from app.http.services.users.user_base_models import UserStatus
from app.http.services.users.user_base_models import UserPermission
from app.http.services.event_channel import (
    subscriber, publisher, Params as PublisherParams, EventRoute
)

log = get_logger("UserService.log")

class UserService:
    def __init__(self, user_repository: UserRepository, redis: RedisInstance) -> None:
        self._repository: UserRepository = user_repository
        self._redis:RedisInstance = redis

    def get_all(self, params: UserParams) -> ResponseList:
        result = self._repository.get_all(params)
        users = []
        for user in result['users']:
            users.append(UsersResponse(
                id=user.id,
                inner_phone=user.inner_phone,
                position=user.position,
                department=user.department,
                fio=user.fio,
                employment_status=user.employment_status
            ))
        return ResponseList(pagination = result['pagination'], users = users)

    def get_user_position(self):
        return self._repository.get_users_position()
    def get_call_by_call_id(self, call_id):
        """ Формирование данных из таблицы cdr для отправки в sutecrm """
        total_billsec = 0
        disposition = ""
        cdrs = self._repository.get_call_by_call_id(call_id=call_id)
        for cdr in cdrs:
            if disposition == "":
                disposition = cdr.disposition
            total_billsec = total_billsec + cdr.billsec
        
        return {
            "billsec": total_billsec,
            "disposition": disposition
        }
    def get_departments_employees(self, department_id):
        department_headers, department_employees = [], []
        users = self._repository.get_users_department(department_id=department_id)
        # TODO: перекрывается ошибка из get_users_department следующей - NotFoundError
        for person in users:
            if person[5] == True:
                department_headers.append(person)
            else:
                department_employees.append(person)
        if not department_headers and not department_employees:
            description = f"Не найдено пользователей в департаменте с ID={department_id}."
            raise NotFoundError(
                entity_message=f"No users in department with id={department_id}",
                entity_id=department_id,
                entity_description=description
            )
        result = {
            "management": department_headers,
            "supervisor": department_employees
        }
        return result

    def get_user_by_id(self, user_id: int, only_access: bool = True):
        user = self._repository.get_by_id(user_id)
        userDetail = self.__user_response(user, only_access)
        password = ""
        for i in range(len(userDetail.password)):
            password += "*"
        userDetail.password = password
        del user
        return userDetail

    def by_id(self, id):
        return self._repository.get_by_id(id)

    def find_user_by_login(self, login: str):
        return self._repository.get_by_login(login) 

    async def create_user(self, user: UserRequest) -> UserDetailResponse:
        user:UserDetailResponse = self._repository.add(self.__fill_fields(user))
        user_param = {
            "id": user.id
        }
        await self._redis.redis.set(f"user:uuid:{user.uuid}", json.dumps(user_param))
        return self.__user_response(user)
    
    async def all(self):
        users = self._repository.items()
        for user in users:
            u = {
                "id": user.id
            }
            await self._redis.redis.set(f"user:uuid:{user.uuid}", json.dumps(u))

    def update_user(self, id: int, user: UserRequest) -> any:
        if id == 0:
            description = f"Не найден пользователь с ID={id}."
            raise UserNotFoundError(entity_id=id, entity_description=description)
        user = self._repository.update(id,self.__fill_fields(user))
        return self.__user_response(user)

    def delete_user_by_id(self, user_id: int) -> None:
        if user_id == 0:
            description = f"Не найден пользователь с ID={id}."
            raise UserNotFoundError(entity_id=user_id, entity_description=description)
        return self._repository.soft_delete(user_id)
    
    def get_all_status_users(self):
        return self._repository.get_all_status()

    async def set_status(self, user_id: int, status_id: int, call_id: str = None):
        status_params = self._repository.set_status(user_id=user_id, status_id=status_id)
        enums = EventRoute
        event = None
        try:
           event = enums[status_params['code'].upper()].value
        except Exception as e:  # TODO: определить тип исключений
            event = "CHANGE_STATUS"
        params = PublisherParams(
            user_id=user_id,
            status_id=status_params['status_id'],
            status_code=status_params['code'],
            status_at=str(status_params['status_at']),
            status=status_params['alter_name'],
            event=event,
            color=status_params['color'],
            call_id=call_id
        )
        await self.__set_status_redis(params)

    async def redis_pub_sub(self, websocket: WebSocket, user_id: int):
            pubsub: PubSub = self._redis.redis.pubsub()
            try:
                channel = f"user:status:{user_id}:c"
                connect_info = await self._repository.user_get_time(user_id)
                async for result in subscriber(pubsub, channel):
                    if result == 1:
                        result = connect_info.json()
                    else:
                        result = result
                    result = json.loads(result)
                    time_kc = datetime.datetime.now() - datetime.datetime.strptime(connect_info.start_time_kc, "%Y-%m-%d %H:%M:%S.%f")
                    # Проболема с датами(разный формат)
                    try:
                        status_at = datetime.datetime.now() - datetime.datetime.strptime(result['status_at'], "%Y-%m-%d %H:%M:%S.%f")
                    except Exception:
                        status_at = datetime.datetime.now() - datetime.datetime.strptime(result['status_at'], "%Y-%m-%d %H:%M:%S")

                    result['start_time_kc'] = convert_second_to_time(time_kc.seconds)
                    result['status_at'] = convert_second_to_time(status_at.seconds)
                    await websocket.send_json(result)
            except ConnectionClosedOK as connection_close:
                log.error(connection_close, stack_info=True)
                return
            except WebSocketDisconnect as web_socket_disconnect:
                log.error(web_socket_disconnect, stack_info=True)
                return
            except Exception as exception:
                log.error(exception, stack_info=True)

    async def add_status_to_redis(self):
        statuses = self._repository.get_all_status()
        for status in statuses:
            status.life_time = str(status.life_time)
            params = status.__dict__
            del params['_sa_instance_state']
            await self._redis.redis.set(f"status:code:{status.code}", json.dumps(params))

    async def set_status_by_aster(
            self, 
            uuid: str, 
            status_code: str, 
            status_time: str, 
            incoming_call: str = None, 
            call_id: str = None,
            script_ivr_hyperscript: str = None
            ):
        """ Используется для установки статуса из астериска """
        status_time = datetime.datetime.fromtimestamp(status_time).__format__("%Y-%m-%d %H:%M:%S.%f")
        status = await self._redis.redis.get(f"status:code:{status_code}")
        user_id = await self._redis.redis.get(f"user:uuid:{uuid}")
        description = f"Пользователь не найден с {uuid}"
        if user_id is None:
            raise NotFoundError(entity_message="user not found", entity_description=description)
        user_id = json.loads(user_id)
        if status is None:
            description = f"Не найден статус"
            raise NotFoundError(entity_message="status not found", entity_description=description)
        status = json.loads(status)
        log.debug(f"uuid={uuid},status_id={status['id']},status_time={status_time}")
        await self._repository.set_status_by_uuid(uuid=uuid,status_id=status['id'],status_time=status_time)
        enums = EventRoute
        event = None
        try:
            event = enums[status['behavior'].upper()].value
        except Exception as e:  # TODO: определить тип исключений
            event = "CHANGE_STATUS"
        params = PublisherParams(
            user_id=user_id['id'],
            status_id=status['id'],
            status_code=status['code'],
            status_at=status_time,
            status=status['alter_name'],
            event=event,
            color=status['color'],
            incoming_call=incoming_call,
            call_id=call_id,
            hyper_script=script_ivr_hyperscript
        )
        await self.__set_status_redis(params)
        if params.status_code == "precall":
            await asyncio.sleep(0.1)
            params.event = "CHANGE_STATUS"
            await self.__set_status_redis(params)

    def dismiss(self, id: int, date_dismissal_at: datetime.datetime = None):
        if date_dismissal_at == None:
            date_dismissal_at = datetime.now()
        self._repository.user_dismiss(id, date_dismissal_at)
        return {
            "message": f"User {id} dismiss : {date_dismissal_at}"
        }

    def recover(self, id: int):
        self._repository.user_recover(id)
        return {
            "message": f"User {id} recover"
        }

    def reset_password(self, id: int, password: str):
        params = {
            "id": id,
            "password": password,
            "hashed_password": sha256(password.encode()).hexdigest()
        }
        self._repository.update_password(params=params)
        return {
            "message": "Password is update"
        }
    
    def set_permission(self, params: UserPermission):
        self._repository.set_permission(params)
        return {
            "message": "rights installation completed successfully"
        }

    async def get_users_status(self, users_id: list):
        result = {}
        for user_id in users_id:
            status = await self._redis.redis.get(f"status.user.{user_id}")
            if status is not None:
                status_params = json.loads(status)
                try:
                    status_code = status_params['status_code']
                except Exception:
                    status_code = status_params['status_cod']
                result[user_id] = UserStatus(
                    status_id=status_params['status_id'],
                    status_cod=status_code,
                    status_at=str(status_params['status_at']),
                    status=status_params['status'],
                    color=status_params['color'],
                )
        return result

    def __fill_fields(self, user: UserRequest):
        user_create = UserModel()
        user_fields = user.__dict__
        for field in user_fields:
            if user_fields[field] == 0:
                user_fields[field] = None
            if field == "hashed_password":
                continue
            user_create.__setattr__(field, user_fields[field])
        user_create.fio = f"{user.last_name} {user.name} {user.patronymic}".strip()
        user_create.hashed_password = sha256(user.password.encode()).hexdigest()
        return user_create

    def __user_response(self, user: UserModel, only_access: bool = False):
        userDetail = UserDetailResponse(
            id=user.id,
            uuid=user.uuid,
            email=user.email,
            login=user.login,
            name=user.name,
            last_name=user.last_name,
            patronymic=user.patronymic,
            fio=user.fio,
            password=user.password,
            date_employment_at=user.date_employment_at,
            date_dismissal_at = user.date_dismissal_at,
            phone=user.phone,
            image_id=user.image_id,
            employment_status=user.employment_status,
            personal_number=user.personal_number
        )
        userDetail.is_operator = user.is_operator
        userDetail.groups = user.groups
        userDetail.skills = user.skills
        userDetail.position = user.position
        status_user = user.status
        if user.inner_phone is not None and user.inner_phone != []:
            userDetail.inner_phone = user.inner_phone[0].phone_number
        if user.position != None:
            userDetail.position = user.position
        if user.department != None:
            userDetail.department = {
                "id":user.department.id,
                "name":user.department.name
            }
        if status_user != None:
            userDetail.status = UserStatus(
                status_id=user.status_id,
                status_cod=user.status.code,
                status_at=str(user.status_at),
                status=user.status.alter_name,
                color=user.status.color,
            )
        if user.image == None:
            userDetail.photo_path = user.image
        else:
            userDetail.photo_path = user.image.path
        result_roles = {}
        user_permission = self._repository.get_user_permission(user.id, only_access)
        if user_permission == {}:
            user_permission = self._repository.get_role_permission(user.id, only_access)
        for role_id, params in user_permission.items():
            if len(params['permissions']) == 0:
                continue
            res = {
                "id": params['id'],
                "name": params['role_name'],
                "access": []
            }
            result_roles[role_id] = res
            permission = []
            for p in params['permissions'].values():
                permission.append({
                    'name': p['name'],
                    'access': p['method_access'],
                    "module_name": p['module_name'],
                    "module_id": p['module_id']
                })
                print(p)
            result_roles[role_id]['access'] = permission
        userDetail.roles = list(result_roles.values())
        del status_user
        return userDetail

    async def __set_status_redis(self, status_info: PublisherParams):
        await self._redis.redis.set(f"status.user.{status_info.user_id}", json.dumps(dict(status_info)))
        channel = f"user:status:{status_info.user_id}:c"
        await publisher(self._redis.redis, channel, dict(status_info))
            
class SkillService:
    def __init__(self, skill_repository: SkillsRepository) -> None:
        self._repository: SkillsRepository = skill_repository
    
    def add(self, text: str):
        return self._repository.add_skill(text)
    
    def find(self, text:str):
        return self._repository.find_skill(text)

__all__ = ('UserService', 'SkillsRepository')
