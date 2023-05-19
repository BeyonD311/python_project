from enum import Enum
from pydantic import BaseModel, validator
from datetime import date, time
from typing import Optional, Dict


class CalculationMethod(Enum):
    SUM = "SUM"
    AVG = "AVG"


class BaseAnalytic(BaseModel):
    beginning: date
    ending: date

    @validator('ending')
    def validate_ending(cls, v, values):
        if 'beginning' in values and v < values['beginning']:
            raise ValueError('Ending date cannot be earlier than beginning date')
        return v


class DisposalAnalytic(BaseAnalytic):
    uuid: str
    calculation_method: CalculationMethod = CalculationMethod.SUM


class AntAnalytic(DisposalAnalytic):
    pass


class CallAnalytic(BaseAnalytic):
    number: str


# class AnalyticResponse(BaseModel):
#     status_code: str
#     delta: str
#
#
# class DisposalResponse(BaseModel):
#     analytic: list[AnalyticResponse]
#
#
# class AntResponse(AnalyticResponse):
#     pass
