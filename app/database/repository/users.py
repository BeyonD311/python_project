from datetime import datetime
from .super import SuperRepository, NotFoundError, Pagination
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
from math import ceil



class UserRepository(SuperRepository): 
    base_model = User
    
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
                                  self.base_model.head_of_depatment,
                                  StatusModel.name.label("status"), StatusModel.color.label("status_color"),
                                  PositionModel.name.label("position"),
                                  DepartmentsModel.name.label("department")
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

    def set_status(self, user_id, status_id):
        with self.session_factory() as session:
            current = session.query(self.base_model).get(user_id)
            current.status_id = status_id
            current.status_at = datetime.now()
            session.add(current)
            session.commit()
            return True

    def add(self, user_model: User) -> any:
        try:
            with self.session_factory() as session:
                user = user_model
                user = self.item_add_or_update(user, session)
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
        print("---------------------------")
        print(user.roles_id)
        print("---------------------------")
        roles = session.query(RolesModel).filter(RolesModel.id.in_(user.roles_id)).all()
        groups = session.query(GroupsModel).filter(GroupsModel.id.in_(user.group_id)).all()
        if user.skills_id != []:
            skills = session.query(SkillsModel).filter(GroupsModel.id.in_(user.skills_id)).all()
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

    def get_pagination(self, query, size, page):
        count_items = query.count()
        total_page = ceil(count_items / size)
        return {
            "pagination": Pagination(
                total_page = total_page,
                total_count = count_items,
                page=page + 1,
                size=size
            )
        }


class UserNotFoundError(NotFoundError):
    entity_name: str = "User"

def after_update_handler(mapper, connection, target):
    print("------------------")
    print(mapper, target, connection)
    print("------------------")

#будем обновлять таблицу
event.listen(UserRepository, 'after_update', after_update_handler)