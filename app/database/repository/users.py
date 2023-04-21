from datetime import datetime, timedelta
from uuid import uuid4
from .super import SuperRepository, NotFoundError
from app.database import UserModel as User
from app.database import RolesModel
from app.database import GroupsModel
from app.database import SkillsModel
from app.database import StatusModel
from app.database import PositionModel
from app.database import DepartmentsModel
from app.database import UsersPermission
from app.database import RolesPermission
from app.database import HeadOfDepartment
from app.database import ImagesModel
from app.database import InnerPhone
from app.database import StatusHistoryModel
from app.http.services.access import Access
from sqlalchemy import and_, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query
from sqlalchemy.engine.base import Connection
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from typing import Callable
from uuid import uuid4
from .asterisk import Asterisk, StatusHistoryParams
from app.http.services.event_channel import Params


""" 
    События для управления статусами
    0 - статус увольнения

"""
event_type = None

class UserRepository(SuperRepository): 
    base_model = User
    
    def __init__(self, 
                 session_factory: Callable[..., AbstractContextManager[Session]],
                 session_asterisk: Callable[..., AbstractContextManager[Session]] = None
                 ) -> None:
        global event_type
        event_type = None
        super().__init__(session_factory)
        self.session_asterisk: Asterisk = Asterisk(session_asterisk)
    def items(self):
        with self.session_factory() as session:
            return session.query(self.base_model).filter(self.base_model.id != 0).all()
    def get_all(self, params) -> dict[User]:
        with self.session_factory() as session:
            offset = 0
            if params.page > 0:
                offset = (params.size * params.page)
            query = session.query(self.base_model.id,
                                  self.base_model.status_id,
                                  self.base_model.status_at,
                                  self.base_model.fio,
                                  PositionModel.name.label("position"),
                                  DepartmentsModel.name.label("department"),
                                  InnerPhone.phone_number.label("inner_phone"),
                                  self.base_model.employment_status,
                                  self.base_model.is_active
                                  )\
                    .join(StatusModel, StatusModel.id == self.base_model.status_id, isouter=True)\
                    .join(PositionModel, PositionModel.id == self.base_model.position_id, isouter=True)\
                    .join(DepartmentsModel, DepartmentsModel.id == self.base_model.department_id, isouter=True)\
                    .join(InnerPhone, and_(InnerPhone.user_id == self.base_model.id, InnerPhone.is_default == True, InnerPhone.is_registration == True), isouter=True)\
                    .filter(self.base_model.id != 0)
            query = self.__filter(query, params=params)
            result = self.get_pagination(query, params.size, params.page)
            query = query.order_by(self.__sort(query, params))\
                    .limit(params.size)\
                    .offset(offset)
            result['query'] = str(query)
            result['users'] = query.all()
            return result

    def get_by_login(self, login: str) -> User:
        with self.session_factory() as session:
            user = session.query(self.base_model).filter(self.base_model.login == login).first()
            if user is None:
                raise UserNotFoundError(login)
            return user
    def get_by_id(self, id: int) -> User:
        with self.session_factory() as session:
            user: User = session.query(self.base_model).filter(self.base_model.id == id).first()
            user.skills
            user.position
            user.department
            user.skills
            user.status 
            user.image
            for role in user.roles:
                role.permissions
            user.groups
            user.groups
            user.inner_phone
            return user
    def get_users_position(self):
        with self.session_factory() as session:
            query = session.query(PositionModel).all()
            if query is None:
                query = []
            return query

    def get_users_department(self, department_id):
        with self.session_factory() as session:
            result = session.query(self.base_model.id,
                                  self.base_model.inner_phone,
                                  self.base_model.fio,
                                  self.base_model.department_id,
                                  self.base_model.status_id,
                                  HeadOfDepartment.is_active.label("head_of_department"),
                                  StatusModel.name.label("status"),
                                  PositionModel.name.label("position"),
                                  ImagesModel.path.label("path_image"),
                                  InnerPhone.phone_number.label("user_inner_phone"),
                                  StatusModel.code.label("status_code"),
                                  self.base_model.status_at.label("status_at"),
                                  StatusModel.alter_name.label("status_name"),
                                  StatusModel.color.label("status_color")
                                  ).distinct(self.base_model.id)\
                    .join(ImagesModel, ImagesModel.id == self.base_model.image_id, isouter=True)\
                    .join(StatusModel, StatusModel.id == self.base_model.status_id, isouter=True)\
                    .join(PositionModel, PositionModel.id == self.base_model.position_id, isouter=True)\
                    .join(HeadOfDepartment, HeadOfDepartment.head_of_department_id == self.base_model.id, isouter=True)\
                    .join(InnerPhone, and_(InnerPhone.user_id == self.base_model.id, InnerPhone.is_default == True, InnerPhone.is_registration == True), isouter=True)\
                    .filter((self.base_model.department_id == department_id) | (HeadOfDepartment.department_id == department_id), self.base_model.status_id !=4)\
                    .filter((PositionModel.id == 1) | (HeadOfDepartment.is_active == True))\
                    .order_by(self.base_model.id).all()
            if result is None:
                raise UserNotFoundError(department_id)
            return result

    def get_user_permission(self, user_id: int, only_access: bool = True)->dict:
        with self.session_factory() as session:
            sql = f"select p.name, p.module_name, up.method_access, r.id role_id, r.name as role_name, up.module_id from users_permission up "\
                    f"join roles r on r.id = up.role_id "\
                    f"join permissions p on p.id = up.module_id "\
                    f"where up.user_id = {user_id} and r.is_active = true "
            result = session.execute(sql).all()
            return self.__parse_permission_query(result, only_access)
    
    def get_role_permission(self, user_id: int, only_access: bool = True):
        with self.session_factory() as session:
            sql = f"select p.name, p.module_name, rp.method_access, r.id role_id, r.name as role_name, rp.module_id from roles_permission rp "\
                    f"join user_roles ur on ur.role_id = rp.role_id "\
                    f"join roles r on r.id = rp.role_id "\
                    f"join permissions p on p.id = rp.module_id "\
                    f"where ur.user_id = {user_id} and r.is_active = true "
            result = session.execute(sql).all()
            return self.__parse_permission_query(result, only_access)
            

    def __parse_permission_query(self, params, only_access: bool = True):
        result = {}
        access = Access()
        for item in params:
            if item[3] not in result:
                result[item[3]] = {
                    "id": item[3],
                    "role_name": item[4],
                    "permissions": {}
                }
            if only_access and int(item[2]) == 0:
                continue
            access.parse(item[2])
            result[item[3]]["permissions"][item[1]] = {
                "name": item[0],
                "method_access": access.get_access_model(),
                "module_name": item[1],
                "module_id": item[5],
            }
        return result
            

    def update(self, id, user_model: User):
        with self.session_factory() as session:
            user = user_model
            current = session.query(self.base_model).filter(self.base_model.id == id).first()
            if current is None:
                raise IntegrityError("Пользователь не найден", "Пользователь не найден", "Пользователь не найден")
            for param in user.__dict__:
                if param == '_sa_instance_state' or param == 'id' or param == 'roles_id':
                    continue
                values = user.__dict__[param]
                current.__setattr__(param, values)
            current.skills_id = user.skills_id
            current.roles_id = user.roles_id
            current.group_id = user.group_id
            if user.skills_id != []:
                current.skills.clear()
            current.roles.clear()
            current.groups.clear()
            current = self.item_add_or_update(current, session)
            current.skills
            current.position
            current.department
            current.skills
            current.status 
            current.image
            for role in user.roles:
                role.permissions
            current.groups
            for role in current.roles:
                role.permissions
            current.groups
            current.inner_phone
            
            return current

    def set_permission(self, params):
        with self.session_factory() as session:
            user: User = session.query(self.base_model).filter(self.base_model.id == params.user_id).first()
            if user == None:
                raise UserNotFoundError(f" Not found user by id: {params.user_id} ")
            user_permission = user.user_permission
            if len(user_permission) > 0:
                [session.delete(p) for p in user.user_permission]
                session.commit()
            access = Access()
            for role in params.role:
                for permission in role.permissions:
                    access.set_access_model(permission.method_access)
                    p = UsersPermission(
                        user_id = user.id,
                        role_id = role.id,
                        method_access = str(access),
                        module_id = permission.module_id
                    )
                    session.add(p)
            session.commit()  


    def get_all_status(self):
        with self.session_factory() as session:
            return session.query(StatusModel).all()

    def get_users_by_id(self, users_id: list):
        with self.session_factory() as session:
            users = session.query(self.base_model).filter(self.base_model.id.in_(users_id)).all()
            if len(users) < 1:
                raise NotFoundError(f"Users not found {users_id}")
            return users

    def set_status(self, user_id, status_id, call_id = None):
        global event_type
        current = None
        
        with self.session_factory() as session:
            current = session.query(self.base_model).get(user_id)
            if status_id == 10:
                if self.session_asterisk.check_device_status(current.uuid):
                    status_id = 10
                else:
                    status_id = 14
            current.status_id = status_id
            current.status_at = datetime.now()
            current.status
            current.inner_phone
            event_type="set_status"
            session.add(current)
            session.commit()
        status_id = current.status_id
        status_code = current.status.code
        if status_id == 15:
            status_id = 14
            status_code = "unavailable"
        if status_code.find("break") != -1:
            status_id = 9
        if current.status_id != 18:
            self.session_asterisk.save_status_asterisk(status_id, current.uuid)
            inner_phone: InnerPhone
            for inner_phone in current.inner_phone:
                if inner_phone.is_default and inner_phone.is_registration:
                    status_history_params = StatusHistoryParams(
                        time_at=int(current.status_at.timestamp()),
                        user_uuid=current.uuid,
                        user_c=str(inner_phone.phone_number),
                        source=0,
                        destination=0,
                        code=status_code
                    )
                    self.session_asterisk.set_status_history(status_history_params)
        self.session_asterisk.execute()
        return {
            "uuid": current.uuid,
            "id": current.id,
            "status_id": current.status_id,
            "status_at": str(current.status_at),
            "status": current.status.name,
            "code": current.status.behavior,
            "color": current.status.color,
            "alter_name": current.status.alter_name,
        }
    
    async def set_status_by_uuid(self, uuid, status_id, status_time):
        global event_type
        with self.session_factory() as session:
            sql = f"update users set status_id = {status_id}, status_at = '{str(status_time)}' where uuid = '{uuid}'"
            event_type="set_status"
            session.execute(sql)
            session.commit()
        self.session_asterisk.save_status_asterisk(status_id,uuid)
        self.session_asterisk.execute()

    def add(self, user_model: User) -> any:
        try:
            with self.session_factory() as session:
                status:StatusModel = session.query(StatusModel).filter(StatusModel.code == 'offline').first()
                user = user_model
                user.uuid = uuid4()
                user = self.item_add_or_update(user, session)
                if status != None:
                    # Сохраняем текущий статус в редис для быстрого доступа
                    user.status_id = status.id
                    user.status_at = datetime.now()
                user.position
                user.department
                user.skills
                user.status
                user.image
                for role in user.roles:
                    role.permissions
                    permission: RolesPermission
                    for permission in role.permission_model:
                        session.add(UsersPermission(
                            user_id = user.id,
                            role_id = permission.role_id,
                            module_id = permission.module_id,
                            method_access = permission.method_access
                        ))
                session.commit()
                user.groups
                user.inner_phone
                return user
        except IntegrityError as e: 
            raise(e)
    def item_add_or_update(self, user: User, session):
        roles = session.query(RolesModel).filter(RolesModel.id.in_(user.roles_id)).all()
        groups = session.query(GroupsModel).filter(GroupsModel.id.in_(user.group_id)).all()
        if user.is_operator and user.skills_id != []:
            skills = session.query(SkillsModel).filter(SkillsModel.id.in_(user.skills_id)).all() 
            [user.skills.append(s) for s in skills]
        elif user.is_operator == False:
            user.skills = []
        [user.roles.append(r) for r in roles]
        [user.groups.append(g) for g in groups]
        session.add(user)
        session.commit()
        return user
    
    def update_password(self, params: dict):
        with self.session_factory() as session:
            user: User = session.query(self.base_model).filter(self.base_model.id == params['id']).first()
            user.password = params['password']
            user.hashed_password = params['hashed_password']
            session.add(user)
            session.commit()
        return True

    def soft_delete(self, id: int, delete_time = None):
        phones = []
        with self.session_factory() as session:
            user = self.get_by_id(id)
            if delete_time is None:
                user.date_dismissal_at = datetime.now()
            else:
                user.date_dismissal_at = delete_time
            user.is_active = False
            for phone in user.inner_phone:
                phones.append(f"{phone.phone_number}")
                session.delete(phone)
            session.add(user)
            session.commit()   
        if phones != []:
            self.session_asterisk.delete_asterisk(",".join(phones))
            self.session_asterisk.execute()
    
    def user_dismiss(self, user_id: int,  date_dismissal_at: datetime = None):
        user = self.get_by_id(user_id)
        global event_type
        event_type = 0
        phones = []
        with self.session_factory() as session:
            status = session.query(StatusModel).filter(StatusModel.code == 'dismiss').first()
            if status == None:
                raise NotFoundError("Не найден статус увольнения")
            user.date_dismissal_at = date_dismissal_at
            user.status_at =  date_dismissal_at
            user.status_id = status.id
            user.employment_status = False
            for phone in user.inner_phone:
                phones.append(str(phone.phone_number))
                session.delete(phone)
            session.add(user)
            session.commit()
        if phones != []:
            self.session_asterisk.delete_asterisk(",".join(phones))
            self.session_asterisk.execute()

    async def user_get_time(self, user_id: int):
        with self.session_factory() as session:
            user = session.query(self.base_model).filter(self.base_model.id == user_id).first()
            date_now = datetime.now().__format__("%Y-%m-%d 00:00:00")
            # the beginning of the working day
            time_kc = session.query(StatusHistoryModel).filter(StatusHistoryModel.user_id == user_id, StatusHistoryModel.status_id == 18, StatusHistoryModel.update_at >= date_now)\
                .order_by(StatusHistoryModel.update_at.asc()).first()
            if time_kc is None:
                time_kc = datetime.now()
            else:
                time_kc = time_kc.update_at
            result = {
                "user_id": user_id,
                "status_id": user.status_id,
                "status_code": user.status.code,
                "status_at": str(user.status_at),
                "status": "",
                "event":"CONNECTION",
                "color": "",
                "start_time_kc": str(time_kc),
                "incoming_call": None
            }
            if user.status is not None:
                result['status'] = user.status.alter_name
                result['color'] = user.status.color
            result = Params(**result)
            return result
        
    def user_recover(self, user_id: int):
            user = self.get_by_id(user_id)
            global event_type
            event_type = "recover"
            with self.session_factory() as session:
                status = session.query(StatusModel).filter(StatusModel.code == 'offline').first()
                if status == None:
                    raise NotFoundError("Не найден статус увольнения")
                user.date_dismissal_at = None
                user.status_at =  datetime.now()
                user.status_id = status.id
                user.employment_status = True
                session.add(user)
                session.commit()

    def user_restore(self, id):
        with self.session_factory() as session:
            user = self.get_by_id(id)
            user.date_dismissal_at = None
            user.is_active = True
            session.add(user)
            session.commit()       
    
    def __filter(self, query: Query, params) -> Query:
        if params.filter is not None:
            if params.filter.fio != None:
                query = query.filter(self.base_model.fio.ilike(f'%{params.filter.fio}%'))
            if params.filter.status != None:
                query = query.filter(self.base_model.status_id.in_(params.filter.status))
            if params.filter.login != None:
                query = query.filter(self.base_model.login == params.filter.login)
            if params.filter.department != None:
                query = query.filter(self.base_model.department_id == params.filter.department)
        return query

    def __sort(self, query: Query, params):
        field = self.base_model.id
        if params.sort_field == "fio":
            field = self.base_model.fio
        elif params.sort_field == "status":
            field = StatusModel.name
        elif params.sort_field == "inner_phone":
            field = self.base_model.inner_phone
        elif params.sort_field == "position":
            field = PositionModel.name
        elif params.sort_field == "department":
            field = DepartmentsModel.name
        
        if params.sort_dir.lower() == "desc":
            field = field.desc()
        else:
            field = field.asc()
        return field


class UserNotFoundError(NotFoundError):
    entity_name: str = "User"

# Обновляем таблицу status_history после обновления статусов
@event.listens_for(User, 'after_update')
def after_update_handler(mapper, connection: Connection, target: User):
    
    def update(time_at = None):
        query_update = f"update status_history set is_active = false"
        if time_at is not None:
            query_update += f", time_at = '{time_at}'"
        query_update += f" where user_id = {target.id} and is_active = true"
        connection.execute(query_update)
    def add(user_id, status_id, update_at, is_active = "true"):
        if status_id == 16 or status_id == 15:
            is_active = "false"
        connection.execute(f"insert into status_history (user_id,status_id,update_at,is_active) values ({user_id},{status_id},'{update_at}',{is_active})")
    if event_type != None:
        with connection.begin():
            status_current = connection.execute(f"select update_at, status_id, user_id from status_history where user_id = {target.id} and is_active = true").first()
            if type(target.status_at) == str:
                target.status_at = datetime.strptime(target.status_at, "%Y-%m-%d %H:%M:%S")
            time_at = None
            if status_current is not None:
                date:datetime = status_current[0]
                td: timedelta = target.status_at - date
                if td.days > 0:
                    DAY = timedelta(1)
                    for i in range(td.days):
                        update("23:59:59")
                        date += DAY
                        add(status_current[2],status_current[1], date)
                    time_at = str(td).split(",")[1]
                else:
                    time_at = str(td)
                update(time_at)
            add(target.id, target.status_id, target.status_at)
