import os
from datetime import datetime
from .super import SuperRepository, NotFoundError
from app.database import UserModel as User, RolesModel, GroupsModel, SkillsModel, StatusModel

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
            where = "where u.id != 0 "
            query = session.query(self.base_model)
            if params.filter is not None:
                params_w = []
                if params.filter.fio != None:
                    params_w.append(f"fio like '{params.filter.fio}'")
                if params.filter.status != None:
                    params_w.append(f"status_id = {params.filter.status}")
                if params.filter.login != None:
                    params_w.append(f"login = '{params.filter.login}'")
                where = "where u.id != 0 and "+" and ".join(params_w)
            if params.page > 0:
                params.page = (params.size * params.page)
            sql = f"select u.id as id, u.fio as fio, d.name as department, p.name as position,u.inner_phone as inner_phone, "\
                    f"su.name as status, su.id as status_id, u.status_at as status_at from users as u "\
                    f"left join departments d on d.id = u.department_id "\
                    f"left join status_users su on su.id = u.status_id "\
                    f"left join position p on p.id = u.position_id "\
                    f"{where} order by {params.sort_field} {sort_d} limit {params.size} offset {params.page}"
            statement = text(sql)
            query = session.execute(statement)
            result['items'] = query.all()
            return result

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
                skills = session.query(SkillsModel).filter(SkillsModel.id.in_(user.skills_id)).all()
                current.roles.clear()
                current.groups.clear()
                current.skills.clear()
                [current.roles.append(r) for r in roles]
                [current.groups.append(g) for g in groups]
                [current.skills.append(s) for s in skills]
                session.add(current)
                session.commit()
                user.__delattr__("hashed_password")
                user.__delattr__("password")
                return user
        except IntegrityError as e:
            os.remove(user_model.photo_path)
            return False, e

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
                roles = session.query(RolesModel).filter(RolesModel.id.in_(user.roles_id)).all()
                groups = session.query(GroupsModel).filter(GroupsModel.id.in_(user.group_id)).all()
                skills = session.query(SkillsModel).filter(GroupsModel.id.in_(user.skills_id)).all()
                [user.roles.append(r) for r in roles]
                [user.groups.append(g) for g in groups]
                [user.skills.append(s) for s in skills]
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