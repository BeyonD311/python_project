import json
from contextlib import AbstractContextManager
from datetime import time
from math import ceil
from sqlalchemy import text
from sqlalchemy.orm import Session
from .super import NotFoundError
from typing import Callable
from app.http.services.schedule.schedule_base_model import ScheduleCreate, ScheduleUpdate, Pagination, Order
from .super import Pagination


class TimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, time):
            return obj.strftime('%H:%M:%S')
        return super().default(obj)


class ScheduleRepository:
    def __init__(self, session_asterisk: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_asterisk = session_asterisk

    def get_by_id(self, schedule_id: int):
        with self.session_asterisk() as session:
            query = text('SELECT * FROM schedule '
                         'WHERE id = :schedule_id;')
            db_schedule = session.execute(query, {'schedule_id': schedule_id}).fetchone()
            if not db_schedule:
                raise NotFoundError(entity_id=schedule_id,
                                    entity_description=f"Schedule with id={schedule_id} not found")
            return db_schedule

    def get_all_by_queue(self, queue_name: str, pagination: Pagination, order: Order):
        with self.session_asterisk() as session:
            query = 'SELECT * FROM schedule ' \
                    'WHERE queue_name = :queue_name ' \
                    f'ORDER BY {order.field} {order.direction} ' \
                    'LIMIT :offset, :size;'
            params = {
                'queue_name': queue_name,
                'offset': (pagination.page - 1) * pagination.size,
                'size': pagination.size
            }
            print(params)
            result = session.execute(text(query), params).fetchall()
            total_count = self.__get_total_count(queue_name=queue_name)
            total_page = ceil(total_count / pagination.size)
            pagination = Pagination(
                page=pagination.page,
                size=pagination.size,
                total_page=total_page,
                total_count=total_count
            )
            return {
                'data': result,
                'pagination': pagination
            }

    def add(self, schedule_data: ScheduleCreate):
        with self.session_asterisk() as session:
            db_schedule = schedule_data.dict()
            query = text('''
                INSERT INTO schedule(queue_name, beginning, ending, active, stop_queue, period_schedule, holiday) 
                VALUES (:queue_name, :beginning, :ending, :active, :stop_queue, :period_schedule, :holiday)
                RETURNING id, beginning, ending, active, stop_queue, period_schedule, holiday;
            ''')
            db_schedule['period_schedule'] = json.dumps(db_schedule['period_schedule'], cls=TimeEncoder)
            result = session.execute(query, db_schedule)
            session.commit()
            return result.fetchone()

    def update(self, schedule_id: int, update_data: ScheduleUpdate):
        with self.session_asterisk() as session:
            db_schedule = {**update_data.dict(), 'id': schedule_id}
            db_schedule['period_schedule'] = json.dumps(db_schedule['period_schedule'], cls=TimeEncoder)
            query = text('UPDATE schedule SET ' + ', '.join(
                [f'{key} = :{key}' for key in db_schedule.keys() if key != 'id']) +
                         ' WHERE id = :id')
            result = session.execute(query, db_schedule)
            if result.rowcount == 0:
                raise NotFoundError(entity_id=schedule_id,
                                    entity_description=f"Schedule with id={schedule_id} not found")
            session.commit()

    def update_status(self, schedule_id: int, status: bool):
        with self.session_asterisk() as session:
            query = 'UPDATE schedule SET active=:status ' \
                    'WHERE id = :schedule_id'
            result = session.execute(text(query), {'status': status, 'schedule_id': schedule_id})
            if result.rowcount == 0:
                raise NotFoundError(entity_id=schedule_id,
                                    entity_description=f"Schedule with id={schedule_id} not found")
            session.commit()

    def delete_by_id(self, schedule_id: int) -> None:
        with self.session_asterisk() as session:
            query = text('DELETE FROM schedule WHERE id = :schedule_id;')
            result = session.execute(query, {'schedule_id': schedule_id})
            if result.rowcount == 0:
                raise NotFoundError(entity_id=schedule_id,
                                    entity_description=f"Schedule with id={schedule_id} not found")
            session.commit()

    def get_active_schedules(self, queue_name: str):
        with self.session_asterisk() as session:
            query = text('''SELECT period_schedule FROM schedule 
                            WHERE schedule.active = TRUE 
                            AND schedule.queue_name = :queue_name
                            AND NOW() BETWEEN beginning AND ending;''')
            return session.execute(query, {'queue_name': queue_name}).all()

    def get_count_of_inclusions(self, beginning: str, ending: str):
        with self.session_asterisk() as session:
            query = '''SELECT COUNT(*) FROM schedule WHERE (beginning <= :ending) AND (:beginning <= ending);'''
            result = session.execute(text(query), {'beginning': beginning, 'ending': ending})
            return result.scalar()

    def is_updated_has_self_inclusion(self, beginning: str, ending: str, update_id: int):
        with self.session_asterisk() as session:
            query = '''SELECT COUNT(*) FROM schedule WHERE (beginning <= :ending) AND (:beginning <= ending)
                                                                AND id = :update_id;'''
            result = session.execute(text(query), {'beginning': beginning, 'ending': ending, 'update_id': update_id})
            r = result.scalar()
            print(r)
            return bool(r)

    def __get_total_count(self, queue_name: str):
        with self.session_asterisk() as session:
            query = 'SELECT COUNT(*) FROM schedule ' \
                    'WHERE queue_name = :queue_name;'
            result = session.execute(text(query), {'queue_name': queue_name})
            return result.scalar()

    def set_queue_status(self, queue_name: str, value: bool):
        with self.session_asterisk() as session:
            query = 'UPDATE queues SET queue_enabled  = :value ' \
                    'WHERE name = :name'

            session.execute(text(query), {'name': queue_name, 'value': value})
            session.commit()

    def get_all_queues_names(self):
        with self.session_asterisk() as session:
            query = 'SELECT name FROM queues'
            return session.execute(text(query)).fetchall()
