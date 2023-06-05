from enum import Enum
from pydantic import BaseModel, validator
from datetime import date, datetime
from typing import Optional, Dict


class CalculationMethod(Enum):
    SUM = "SUM"
    AVG = "AVG"


class BaseAnalytic(BaseModel):
    beginning: datetime
    ending: datetime

    @validator('ending')
    def validate_ending(cls, v, values):
        if 'beginning' in values and v < values['beginning']:
            raise ValueError('Ending date cannot be earlier than beginning date')
        return v


class DisposalAnalytic(BaseAnalytic):
    user_id: int
    calculation_method: CalculationMethod = CalculationMethod.SUM


class AntAnalytic(DisposalAnalytic):
    pass 


class CallAnalytic(BaseAnalytic):
    user_id: int

class QualityAnalytic(DisposalAnalytic):
    pass


class TotalRatingNums(BaseModel):
    name: str
    value: int

class QualityAnalyticResponse(BaseModel):
    data: list[TotalRatingNums]
    totalData: dict


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
