import datetime
import json
from datetime import datetime
from app.http.services.schedule.schedule_base_model import ScheduleCreate, ScheduleUpdate
from app.database import ScheduleRepository


class ScheduleService:
    def __init__(self, schedule_repository: ScheduleRepository) -> None:
        self._repository = schedule_repository

    def get_all_by_priority(self, queue_name: str):
        return self._repository.get_all_by_priority(queue_name=queue_name)

    def get_by_id(self, schedule_id: int):
        return self._repository.get_by_id(schedule_id=schedule_id)

    def get_all_by_queue_name(self, queue_name: str):
        return self._repository.get_all_by_queue(queue_name=queue_name)

    def create(self, schedule: ScheduleCreate):
        return self._repository.add(schedule_data=schedule)

    def update(self, update_data: ScheduleUpdate):
        return self._repository.update(update_data=update_data)

    def delete(self, schedule_id: int):
        return self._repository.delete_by_id(schedule_id=schedule_id)

    def is_active_now(self, queue_name: str):
        active_schedules = self._repository.get_active_schedules(queue_name=queue_name)
        if active_schedules:
            for active_schedule in active_schedules:
                period_schedule = json.loads(active_schedule[0])
                periods = ((datetime.strptime(period[0], '%H:%M:%S').time(),
                            datetime.strptime(period[1], '%H:%M:%S').time())
                           for period in period_schedule[str(datetime.today().weekday() + 1)])
                if any(start <= datetime.now().time() <= end for start, end in periods):
                    return True
        return False
