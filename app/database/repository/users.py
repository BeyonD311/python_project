from datetime import datetime, timedelta
from .super import SuperRepository, NotFoundError
from app.database import UserModel as User
from app.database import RolesModel
from app.database import GroupsModel
from app.database import SkillsModel
from app.database import StatusModel
from app.database import PositionModel
from app.database import DepartmentsModel
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query
from sqlalchemy.engine.base import Connection
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from typing import Callable


""" 
    События для управления статусами
    0 - статус увольнения

"""
event_type = None

class UserRepository(SuperRepository): 
    base_model = User
    
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        global event_type
        event_type = None
        super().__init__(session_factory)

    def get_all(self, params) -> dict[User]:
        with self.session_factory() as session:
            offset = 0
            if params.page > 0:
                offset = (params.size * params.page)
            query = session.query(self.base_model.id,
                                  self.base_model.status_id,
                                  self.base_model.status_at,
                                  self.base_model.inner_phone,
                                  self.base_model.fio,
                                  StatusModel.name.label("status"), StatusModel.color.label("status_color"),
                                  PositionModel.name.label("position"),
                                  DepartmentsModel.name.label("department"),
                                  self.base_model.employment_status
                                  )\
                    .join(StatusModel, StatusModel.id == self.base_model.status_id, isouter=True)\
                    .join(PositionModel, PositionModel.id == self.base_model.position_id, isouter=True)\
                    .join(DepartmentsModel, DepartmentsModel.id == self.base_model.department_id, isouter=True)\
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
            print("-------------------------------")
            print(user)
            print("-------------------------------")

            if user is None:
                raise UserNotFoundError(login)
            return user

    def get_users_position(self):
        with self.session_factory() as session:
            query = session.query(PositionModel).all()
            if query is None:
                query = []
            return query

    def get_by_id(self, user_id: int) -> User:
        return super().get_by_id(user_id)

    def get_user_permission(self, user_id: int)->dict:
        with self.session_factory() as session:
            sql = f"select p.module_name, rp.method_access  from users u "\
                    f"left join user_roles ur on ur.user_id = u.id "\
                    f"left join roles_permission rp on rp.role_id = ur.role_id "\
                    f"left join permissions p on p.id = rp.module_id " \
                    f"where u.id = {user_id}"
            result = {}
            for item in session.execute(sql).all():
                result[item[0]] = {
                    "method_access": item[1]
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
            current.deparment
            current.skills
            current.status 
            current.image
            for role in user.roles:
                role.permissions
            current.groups
            for role in current.roles:
                role.permissions
            current.groups
            
            return current

    def get_all_status(self):
        with self.session_factory() as session:
            return session.query(StatusModel).all()

    def get_users_by_id(self, users_id: list):
        with self.session_factory() as session:
            users = session.query(self.base_model).filter(self.base_model.id.in_(users_id)).all()
            if len(users) < 1:
                raise NotFoundError(f"Users not found {users_id}")
            return users

    def set_status(self, user_id, status_id):
        global event_type
        with self.session_factory() as session:
            current = session.query(self.base_model).get(user_id)
            current.status_id = status_id
            current.status_at = datetime.now()
            event_type="set_status"
            session.add(current)
            session.commit()
            return {
                "id": current.id,
                "status_id": current.status_id,
                "status_at": str(current.status_at),
                "color": current.status.color,
                "status": current.status.name
            }

    def add(self, user_model: User) -> any:
        try:
            with self.session_factory() as session:
                status:StatusModel = session.query(StatusModel).filter(StatusModel.name.ilike("оффлайн")).first()
                user = user_model
                user = self.item_add_or_update(user, session)
                if status != None:
                    # Сохраняем текущий статус в редис для быстрого доступа
                    user.status_id = status.id
                    user.status_at = datetime.now()
                user.position
                user.deparment
                user.skills
                user.status
                user.image
                for role in user.roles:
                    role.permissions
                user.groups
                return user
        except IntegrityError as e: 
            raise(e)
    def item_add_or_update(self, user: User, session):
        roles = session.query(RolesModel).filter(RolesModel.id.in_(user.roles_id)).all()
        groups = session.query(GroupsModel).filter(GroupsModel.id.in_(user.group_id)).all()
        if user.skills_id != []:
            skills = session.query(SkillsModel).filter(SkillsModel.id.in_(user.skills_id)).all() 
            [user.skills.append(s) for s in skills]
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
        with self.session_factory() as session:
            user = self.get_by_id(id)
            if delete_time is None:
                user.date_dismissal_at = datetime.now()
            else:
                user.date_dismissal_at = delete_time
            user.is_active = False
            session.add(user)
            session.commit()       
    
    def user_dismiss(self, user_id: int,  date_dismissal_at: datetime = None):
        user = self.get_by_id(user_id)
        global event_type
        event_type = 0
        with self.session_factory() as session:
            status = session.query(StatusModel).filter(StatusModel.name.ilike('уволен')).first()
            if status == None:
                raise NotFoundError("Не найден статус увольнения")
            user.date_dismissal_at = date_dismissal_at
            user.status_at =  date_dismissal_at
            user.status_id = status.id
            session.add(user)
            session.commit()

    def user_recover(self, user_id: int):
            user = self.get_by_id(user_id)
            global event_type
            event_type = "recover"
            with self.session_factory() as session:
                status = session.query(StatusModel).filter(StatusModel.name.ilike('оффлайн')).first()
                if status == None:
                    raise NotFoundError("Не найден статус увольнения")
                user.date_dismissal_at = None
                user.status_at =  datetime.now()
                user.status_id = status.id
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
            if params.filter.deparment != None:
                query = query.filter(self.base_model.department_id == params.filter.deparment)
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
    def add(user_id, status_id, update_at):
        connection.execute(f"insert into status_history (user_id,status_id,update_at,is_active) values ({user_id},{status_id},'{update_at}',true)")

    if event_type != None:
        with connection.begin():
            status_current = connection.execute(f"select update_at, status_id, user_id from status_history where user_id = {target.id} and is_active = true").first()
            target.status_at = datetime.now()
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
