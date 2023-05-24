from datetime import timedelta
from typing import Union

from app.database import AnalyticsRepository, InnerPhones, UserRepository
from app.http.services.analytics.analytics_base_model import DisposalAnalytic, AntAnalytic, CallAnalytic


class AnalyticsService:
    def __init__(self, analytics_repository: AnalyticsRepository,
                 inner_phone_repository: InnerPhones,
                 user_repository: UserRepository,
                 disposal_status_codes: list[str],
                 ant_status_codes: list[str],
                 call_dispositions: list[str]
                 ) -> None:
        self._repository = analytics_repository
        self._inner_phones_repository = inner_phone_repository
        self._user_repository = user_repository
        self._disposal_status_codes = disposal_status_codes
        self._ant_status_codes = ant_status_codes
        self._call_dispositions = call_dispositions

    def get_disposal_analytic(self, data: DisposalAnalytic):
        uuid = self._user_repository.get_uuid_by_id(user_id=data.user_id)
        result = self._repository.get_disposal_analytic(uuid=uuid,
                                                        calculation_method=data.calculation_method.value,
                                                        beginning=data.beginning,
                                                        ending=data.ending)
        disposal_data = self._fill_empty_data(status_codes=self._disposal_status_codes, analytic_data=result)
        return self._get_total_data_for_disposal(disposal_data=disposal_data)

    def get_ant_analytic(self, data: AntAnalytic):
        uuid = self._user_repository.get_uuid_by_id(user_id=data.user_id)
        result = self._repository.get_ant_analytic(uuid=uuid,
                                                   calculation_method=data.calculation_method.value,
                                                   beginning=data.beginning,
                                                   ending=data.ending)
        ant_data = self._fill_empty_data(status_codes=self._ant_status_codes, analytic_data=result)
        return self._get_total_data_for_ant(ant_data=ant_data, user_id=data.user_id)

    def get_call_analytic(self, data: CallAnalytic):
        phone = self._inner_phones_repository.get_phone_by_id(user_id=data.user_id)
        result = self._repository.get_call_analytic(phone=phone,
                                                    beginning=data.beginning,
                                                    ending=data.ending)
        analytic_data = self._fill_empty_data_for_call(dispositions=self._call_dispositions, analytic_data=result)
        return {
            'data': analytic_data,
            'totalData': {
                'name': 'callsCount',
                'value': sum([data['call_count'] for data in analytic_data])
            }
        }

    @staticmethod
    def _fill_empty_data(status_codes: list[str], analytic_data: Union[DisposalAnalytic, AntAnalytic]):
        data = [dict(row) for row in analytic_data]
        existed_statuses = [row['name'] for row in data]
        for code in status_codes:
            if code not in existed_statuses:
                data.append({'name': code, 'textValue': '00:00:00', 'value': timedelta(seconds=0)})
        return data

    @staticmethod
    def _fill_empty_data_for_call(dispositions: list[str], analytic_data: CallAnalytic):
        data = [dict(row) for row in analytic_data]
        existed_statuses = [row['disposition'] for row in data]
        for disposition in dispositions:
            if disposition not in existed_statuses:
                data.append({'disposition': disposition, 'call_count': 0})
        return data

    def _get_total_data_for_ant(self, ant_data: list[dict], user_id: int):
        total_sec = sum(int(item['value'].total_seconds()) for item in ant_data)
        avg_sec = round(total_sec / len(ant_data))
        phone_number = self._inner_phones_repository.get_phone_by_id(user_id=user_id)
        calls_count = self._repository.get_call_count(phone_number=phone_number)
        return {
            'data': ant_data,
            'totalData': [
                {
                    'name': 'averageTime',
                    'value': self._convert_from_sec_to_text_format(sec=avg_sec)
                },
                {
                    'name': 'sumTime',
                    'value': self._convert_from_sec_to_text_format(sec=total_sec)
                },
                {
                    'name': 'callsCount',
                    'value': calls_count
                }
            ]
        }

    def _get_total_data_for_disposal(self, disposal_data: list[dict]):
        total_time_sec = sum(int(item['value'].total_seconds()) for item in disposal_data)
        break_time_sec = sum(
            int(item['value'].total_seconds()) for item in disposal_data if item['name'].startswith('break'))
        return {
            'data': disposal_data,
            'totalData': [
                {
                    'name': 'totalTime',
                    'value': self._convert_from_sec_to_text_format(sec=total_time_sec)
                },
                {
                    'name': 'breakTime',
                    'value': self._convert_from_sec_to_text_format(sec=break_time_sec)
                }
            ]
        }

    @staticmethod
    def _convert_from_sec_to_text_format(sec: int):
        hours = sec // 3600
        minutes = (sec % 3600) // 60
        seconds = sec % 60
        time_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

        return time_str
