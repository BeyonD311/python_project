from datetime import date
from app.database import AnalyticsRepository
from app.http.services.analytics.analytics_base_model import DisposalAnalytic, AntAnalytic, CallAnalytic


class AnalyticsService:
    def __init__(self, analytics_repository: AnalyticsRepository) -> None:
        self._repository = analytics_repository

    def get_disposal_analytic(self, data: DisposalAnalytic):
        return self._repository.get_disposal_analytic(uuid=data.uuid,
                                                      calculation_method=data.calculation_method.value,
                                                      beginning=data.beginning,
                                                      ending=data.ending)

    def get_ant_analytic(self, data: AntAnalytic):
        return self._repository.get_ant_analytic(uuid=data.uuid,
                                                 calculation_method=data.calculation_method.value,
                                                 beginning=data.beginning,
                                                 ending=data.ending)

    def get_call_analytic(self, data: CallAnalytic):
        return self._repository.get_call_analytic(number=data.number,
                                                  beginning=data.beginning,
                                                  ending=data.ending)