import json
from contextlib import AbstractContextManager
from datetime import time
from sqlalchemy import text
from sqlalchemy.orm import Session
from .super import NotFoundError
from typing import Callable
from app.http.services.schedule.schedule_base_model import ScheduleCreate, ScheduleUpdate


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
            query = text('SELECT * FROM schedule WHERE id = :schedule_id')
            db_schedule = session.execute(query, {'schedule_id': schedule_id}).first()
            if not db_schedule:
                raise NotFoundError(f"Schedule with id={schedule_id} not found")
            return db_schedule

    def get_all_by_queue(self, queue_name: str):
        with self.session_asterisk() as session:
            query = f'SELECT * FROM schedule WHERE queue_name = :queue_name'
            return session.execute(query, {'queue_name': queue_name}).all()

    def add(self, schedule_data: ScheduleCreate):
        with self.session_asterisk() as session:
            db_schedule = schedule_data.dict()
            query = text('''
                INSERT INTO schedule(queue_name, beginning, ending, active, stop_queue, period_schedule) 
                VALUES (:queue_name, :beginning, :ending, :active, :stop_queue, :period_schedule)
                RETURNING id, beginning, ending, active, stop_queue, period_schedule
            ''')
            db_schedule['period_schedule'] = json.dumps(db_schedule['period_schedule'], cls=TimeEncoder)
            result = session.execute(query, db_schedule)
            session.commit()
            return result.fetchone()

    def update(self, update_data: ScheduleUpdate):
        with self.session_asterisk() as session:
            db_schedule = update_data.dict()
            query = 'UPDATE schedule SET ' + ', '.join([f'{key} = :{key}' for key in db_schedule.keys() if key != 'id'])
            query += ' WHERE id = :id'
            db_schedule['period_schedule'] = json.dumps(db_schedule['period_schedule'], cls=TimeEncoder)
            session.execute(query, db_schedule)
            session.commit()

    def delete_by_id(self, schedule_id: int) -> None:
        with self.session_asterisk() as session:
            query = text('DELETE FROM shcedule WHERE id = :schedule_id')
            session.execute(query, {'schedule_id': schedule_id})
            session.commit()

    def get_active_schedules(self, queue_name: str):
        with self.session_asterisk() as session:
            query = text('''SELECT period_schedule FROM schedule 
                        WHERE schedule.active = TRUE 
                        AND schedule.queue_name = :queue_name
                        AND NOW() BETWEEN beginning AND ending''')
            return session.execute(query, {'queue_name': queue_name}).all()
