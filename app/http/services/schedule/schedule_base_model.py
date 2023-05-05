from pydantic import BaseModel, validator
from datetime import date, time
from typing import Optional, Dict


class ScheduleBase(BaseModel):
    queue_name: str
    beginning: date
    ending: date
    active: Optional[bool] = None
    stop_queue: Optional[str] = None
    period_schedule: Dict[int, list[list[time, time]]] = None
    holiday: Optional[bool] = None

    @validator('queue_name')
    def validate_queue_name(cls, v: str):
        r = v.replace(" ", "_")
        return r

    @validator('ending')
    def validate_ending(cls, v, values):
        if 'beginning' in values and v < values['beginning']:
            raise ValueError('Ending date cannot be earlier than beginning date')
        return v

    @validator('period_schedule')
    def validate_period_schedule(cls, v: dict):
        if v is not None:
            for day, periods in v.items():
                if day not in (0, 1, 2, 3, 4, 5, 6):
                    raise ValueError('Keys must be integer from 0 to 6')

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


class ScheduleUpdate(ScheduleBase):
    pass


class Order(BaseModel):
    field: str
    direction: str


class Pagination(BaseModel):
    page: int
    size: int
