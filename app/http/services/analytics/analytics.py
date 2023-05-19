from datetime import date, timedelta
from app.database import AnalyticsRepository
from app.http.services.analytics.analytics_base_model import DisposalAnalytic, AntAnalytic, CallAnalytic


class AnalyticsService:
    def __init__(self, analytics_repository: AnalyticsRepository) -> None:
        self._repository = analytics_repository
        self._disposal_status_codes = ['break', 'break_lunch', 'break_toilet', 'break_training']
        self._ant_status_codes = ['precall', 'aftercall', 'externalcall', 'callwaiting']
        self._call_dispositions = ['ANSWERED', 'NO ANSWER', 'BUSY']

    def get_disposal_analytic(self, disposal_data: DisposalAnalytic):
        result = self._repository.get_disposal_analytic(uuid=disposal_data.uuid,
                                                        calculation_method=disposal_data.calculation_method.value,
                                                        beginning=disposal_data.beginning,
                                                        ending=disposal_data.ending)
        return self._fill_empty_data_disposal(status_codes=self._disposal_status_codes, analytic_data=result)

    def get_ant_analytic(self, data: AntAnalytic):
        result = self._repository.get_ant_analytic(uuid=data.uuid,
                                                   calculation_method=data.calculation_method.value,
                                                   beginning=data.beginning,
                                                   ending=data.ending)
        return self._fill_empty_data_ant(status_codes=self._ant_status_codes, analytic_data=result)

    def get_call_analytic(self, data: CallAnalytic):
        result = self._repository.get_call_analytic(number=data.number,
                                                    beginning=data.beginning,
                                                    ending=data.ending)
        analytic_data = self._fill_empty_data_for_call(dispositions=self._call_dispositions, analytic_data=result)
        return {
            'detail': analytic_data,
            'total_count': sum([data['call_count'] for data in analytic_data])
        }

    @staticmethod
    def _fill_empty_data_disposal(status_codes: list[str], analytic_data: DisposalAnalytic):
        data = [dict(row) for row in analytic_data]
        existed_statuses = [row['status_code'] for row in data]
        for code in status_codes:
            if code not in existed_statuses:
                data.append({'status_code': code, 'delta_time': '00:00:00'})
        return data

    @staticmethod
    def _fill_empty_data_ant(status_codes: list[str], analytic_data: AntAnalytic):
        data = [dict(row) for row in analytic_data]
        existed_statuses = [row['status_code'] for row in data]
        for code in status_codes:
            if code not in existed_statuses:
                data.append({'status_code': code, 'delta': '00:00:00'})
        return data

    @staticmethod
    def _fill_empty_data_for_call(dispositions: list[str], analytic_data: CallAnalytic):
        data = [dict(row) for row in analytic_data]
        existed_statuses = [row['disposition'] for row in data]
        for disposition in dispositions:
            if disposition not in existed_statuses:
                data.append({'disposition': disposition, 'call_count': 0})
        return data
