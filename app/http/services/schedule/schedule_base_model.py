from pydantic import BaseModel, validator
from datetime import date, time
from typing import Optional, Dict


class ScheduleBase(BaseModel):
    queue_name: str
    beginning: date
    ending: date
    active: Optional[bool] = None
    stop_queue: Optional[str] = None
    period_schedule: Dict[str, list[list[time, time]]] = None

    @validator('period_schedule')
    def validate_period_schedule(cls, v: dict):
        if v is not None:
            for day, periods in v.items():
                for period in periods:
                    if len(period) == 2:
                        if period[0] > period[1]:
                            raise ValueError('Start time can\'t be greater than end time')
                    elif len(period) > 2:
                        raise ValueError('Period must have only start and end')
                    elif len(period) == 1:
                        raise ValueError('Period must have start and end')
        return v


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleRead(ScheduleBase):
    id: int


class ScheduleUpdate(ScheduleRead):
    pass
