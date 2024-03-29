import datetime
import json
from datetime import datetime
from app.http.services.schedule.schedule_base_model import ScheduleCreate, ScheduleUpdate, Pagination, Order
from app.database import ScheduleRepository


class ScheduleService:
    def __init__(self, schedule_repository: ScheduleRepository) -> None:
        self._repository = schedule_repository

    def get_by_id(self, schedule_id: int):
        return self._repository.get_by_id(schedule_id=schedule_id)

    def get_all_by_queue_name(self, queue_name: str, pagination: Pagination, order: Order):
        return self._repository.get_all_by_queue(queue_name=queue_name,
                                                 pagination=pagination,
                                                 order=order)

    def create(self, schedule: ScheduleCreate):
        schedule.period_schedule = self._fill_gave_data_in_periods(periods=schedule.period_schedule)
        inclusions_count = self._repository.get_count_of_inclusions(beginning=schedule.beginning,
                                                                    ending=schedule.ending,
                                                                    queue_name=schedule.queue_name)
        if inclusions_count:
            raise ValueError(f'This schedule overlaps with existing')
        return self._repository.add(schedule_data=schedule)

    def update(self, schedule_id: int, update_data: ScheduleUpdate):
        update_data.period_schedule = self._fill_gave_data_in_periods(periods=update_data.period_schedule)
        inclusions_count = self._repository.get_count_of_inclusions(beginning=update_data.beginning,
                                                                    ending=update_data.ending,
                                                                    queue_name=update_data.queue_name)
        is_include = self._repository.is_updated_has_self_inclusion(beginning=update_data.beginning,
                                                                    ending=update_data.ending,
                                                                    update_id=schedule_id,
                                                                    queue_name=update_data.queue_name)
        if is_include:
            inclusions_count -= 1
        if inclusions_count:
            raise ValueError(f'This schedule overlaps with existing')
        return self._repository.update(schedule_id=schedule_id, update_data=update_data)

    def delete(self, schedule_id: int):
        return self._repository.delete_by_id(schedule_id=schedule_id)

    def is_active_now(self, queue_name: str):
        active_schedules = self._repository.get_active_schedules(queue_name=queue_name)
        if active_schedules:
            for active_schedule in active_schedules:
                period_schedule = json.loads(active_schedule[0])
                periods = ((datetime.strptime(period[0], '%H:%M:%S').time(),
                            datetime.strptime(period[1], '%H:%M:%S').time())
                           for period in period_schedule[str(datetime.today().weekday())])
                if any(start <= datetime.now().time() <= end for start, end in periods):
                    return True
        return False

    def update_status(self, schedule_id: int, status: bool):
        return self._repository.update_status(schedule_id=schedule_id, status=status)

    def turn_on_queue(self, queue_name: str):
        self._repository.set_queue_status(queue_name=queue_name, value=True)

    def turn_off_queue(self, queue_name: str):
        self._repository.set_queue_status(queue_name=queue_name, value=False)

    def get_all_queue_names(self):
        return self._repository.get_all_queues_names()

    def _fill_gave_data_in_periods(self, periods):
        template = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
        template.update(periods)
        return template
