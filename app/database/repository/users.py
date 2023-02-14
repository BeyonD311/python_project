import os
from datetime import datetime
from .super import SuperRepository, NotFoundError
from app.database import UserModel as User
from app.database import RolesModel
from app.database import GroupsModel
from app.database import SkillsModel
from app.database import StatusModel
from app.database import DepartmentsModel
from app.database import EmployeesModel
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
            where = "where u.id != 0 and u.is_active = true"
            query = session.query(self.base_model)
            if params.filter is not None:
                params_w = []
                if params.filter.fio != None:
                    params_w.append(f"fio ilike '%{params.filter.fio}%'")
                if params.filter.status != None:
                    params_w.append(f"status_id = {params.filter.status}")
                if params.filter.login != None:
                    params_w.append(f"login = '{params.filter.login}'")
                where = "where u.id != 0 and "+" and ".join(params_w)
            if params.page > 0:
                params.page = (params.size * params.page)
            sql = f"select u.id as id, u.fio as fio, d.name as department, p.name as position,u.inner_phone as inner_phone, "\
                    f"su.name as status, su.id as status_id, u.status_at as status_at from users as u "\
                    f"left join employees e on e.user_id = u.id "\
                    f"left join departments d on d.id = e.department_id "\
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
                current.skills_id = user.skills_id
                current.roles_id = user.roles_id
                current.group_id = user.group_id
                if user.skills_id != []:
                    current.skills.clear()
                if user.deparment_id != []:
                    current.deparment.clear()
                current.roles.clear()
                current.groups.clear()
                self.item_add_or_update(current, session)
                return current
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
                self.item_add_or_update(user, session)
                user.__delattr__("hashed_password")
                user.__delattr__("password")
                return user
        except IntegrityError as e: 
            if user_model.photo_path is not None:
                os.remove(user_model.photo_path)
            return False, e
    def item_add_or_update(self, user: User, session):
        roles = session.query(RolesModel).filter(RolesModel.id.in_(user.roles_id)).all()
        groups = session.query(GroupsModel).filter(GroupsModel.id.in_(user.group_id)).all()
        if user.deparment_id:
            departments = session.query(DepartmentsModel).filter(DepartmentsModel.id.in_(user.deparment_id)).all()
            print(user.deparment_id)
            [user.deparment.append(d) for d in departments]
        if user.skills_id != []:
            skills = session.query(SkillsModel).filter(GroupsModel.id.in_(user.skills_id)).all()
            [user.skills.append(s) for s in skills]
        [user.roles.append(r) for r in roles]
        [user.groups.append(g) for g in groups]
        session.add(user)
        session.commit()
        return user
class UserNotFoundError(NotFoundError):
    entity_name: str = "User"