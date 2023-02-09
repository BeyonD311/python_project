import os
from .super import SuperRepository, NotFoundError
from app.database import UserModel as User, UserRoles, RolesModel, GroupsModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

class UserRepository(SuperRepository): 
    base_model = User
    
    def get_all(self, params) -> dict[User]:
        with self.session_factory() as session:
            result = self.get_pagination(session, params.page, params.size)
            sort_d = "asc"
            if params.sort_dir.lower() == "desc":
                sort_d = params.sort_dir.lower()
            # result['items'] = session.execute(f"select usersid, ")
            where = ""
            if params.filter is not None:
                print(params.filter)
            if params.page > 1:
                params.page * params.size
            statement = text(f"select u.id as id, u.fio as fio, d.name as department, p.name as position,u.inner_phone as inner_phonefrom users as uleft join departments d on d.id = u.department_id left join position p on p.id = u.position_idleft join status_users su on su.id = u.status_id {where} order by {params.sort_field} {sort_d} limit {params.page} offset {params.size}")
            print(statement)
            # result['items'] = result['items'].order_by(sort).limit(params.size).offset(params.page).all()
            return []

    def get_by_login(self, login: str) -> User:
        with self.session_factory() as session:
            user = session.query(self.base_model).filter(self.base_model.login == login).first()
            if user is None:
                raise UserNotFoundError(login)
            return user

    def get_by_id(self, user_id: int) -> User:
        return super().get_by_id(user_id)

    def update(self, user_model: User):
        try:
            with self.session_factory() as session:
                user = user_model
                current = session.query(self.base_model).filter(self.base_model.id == user.id).first()
                if current is None:
                    raise IntegrityError("Пользователь не найден", "Пользователь не найден", "Пользователь не найден")
                for param in user.__dict__:
                    if param == '_sa_instance_state' or param == 'id' or param == 'roles_id':
                        continue
                    values = user.__dict__[param]
                    current.__setattr__(param, values)
                roles = session.query(RolesModel).filter(RolesModel.id.in_(user.roles_id)).all()
                groups = session.query(GroupsModel).filter(GroupsModel.id.in_(user.group_id)).all()
                current.roles.clear()
                current.groups.clear()
                [current.roles.append(r) for r in roles]
                [current.groups.append(g) for g in groups]
                session.add(current)
                session.commit()
                user.__delattr__("hashed_password")
                user.__delattr__("password")
                return user
        except IntegrityError as e:
            os.remove(user_model.photo_path)
            return False, e

    def add(self, user_model: User) -> any:
        try:
            with self.session_factory() as session:
                user = user_model
                roles = session.query(RolesModel).filter(RolesModel.id.in_(user.roles_id)).all()
                groups = session.query(GroupsModel).filter(GroupsModel.id.in_(user.group_id)).all()
                [user.roles.append(r) for r in roles]
                [user.groups.append(g) for g in groups]
                session.add(user)
                session.commit()
                session.flush()
                user.__delattr__("hashed_password")
                user.__delattr__("password")
                return user
        except IntegrityError as e:
            if user_model.photo_path is not None:
                os.remove(user_model.photo_path)
            return False, e

class UserNotFoundError(NotFoundError):
    entity_name: str = "User"