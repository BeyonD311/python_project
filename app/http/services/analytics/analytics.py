from datetime import timedelta
from typing import Union

from app.database import AnalyticsRepository, InnerPhones, UserRepository
from app.http.services.analytics.analytics_base_model import (
    DisposalAnalytic, AntAnalytic, CallAnalytic, QualityAnalytic, QualityAnalyticResponse, TotalRatingNums
)


class AnalyticsService:
    def __init__(self, analytics_repository: AnalyticsRepository,
                 inner_phone_repository: InnerPhones,
                 user_repository: UserRepository,
                 disposal_statuses: dict,
                 ant_statuses: dict,
                 call_dispositions: dict
                 ) -> None:
        self._repository = analytics_repository
        self._inner_phones_repository = inner_phone_repository
        self._user_repository = user_repository
        self._disposal_status_codes = disposal_statuses
        self._ant_status_codes = ant_statuses
        self._call_dispositions = call_dispositions

    def get_disposal_analytic(self, data: DisposalAnalytic):
        uuid = self._user_repository.get_uuid_by_id(user_id=data.user_id)
        result = self._repository.get_disposal_analytic(uuid=uuid,
                                                        calculation_method=data.calculation_method.value,
                                                        beginning=data.beginning,
                                                        ending=data.ending)
        disposal_data = self._fill_empty_data(status_data=self._disposal_status_codes, analytic_data=result)
        return self._get_total_data_for_disposal(disposal_data=disposal_data)

    def get_ant_analytic(self, data: AntAnalytic):
        uuid = self._user_repository.get_uuid_by_id(user_id=data.user_id)
        result = self._repository.get_ant_analytic(uuid=uuid,
                                                   calculation_method=data.calculation_method.value,
                                                   beginning=data.beginning,
                                                   ending=data.ending)
        ant_data = self._fill_empty_data(status_data=self._ant_status_codes, analytic_data=result)
        return self._get_total_data_for_ant(ant_data=ant_data, user_id=data.user_id, beginning=data.beginning,ending=data.ending)

    def get_call_analytic(self, data: CallAnalytic):
        phones = self._inner_phones_repository.get_phone_by_id(user_id=data.user_id)
        if phones is None:
            phones = []
        result = self._repository.get_call_analytic(phones=phones,
                                                    beginning=data.beginning,
                                                    ending=data.ending)
        analytic_data = self._fill_empty_data(status_data=self._call_dispositions, analytic_data=result)
        return {
            'data': analytic_data,
            'totalData': {
                'name': 'callsCount',
                'value': sum([data['value'] for data in analytic_data]),
                'description': 'Количество звонков'
            }
        }

    def get_call_quality_assessment(self, data: QualityAnalytic):
        phone = self._inner_phones_repository.get_phone_by_id(user_id=data.user_id)
        if phone is None:
            phone = []
        nums_of_rating = self._repository.get_call_quality_assessment(phones=phone,
                                                              calculation_method=data.calculation_method.value,
                                                              beginning=data.beginning,
                                                              ending=data.ending)
        total_call = self._repository.get_call_count(phone_number=phone,
                                                    beginning=data.beginning,
                                                    ending=data.ending)
        result = []
        total_nums_rating = 0
        for rating in nums_of_rating:
            if rating.id == 0:
                continue
            total_nums_rating = total_nums_rating + rating.num_of_rating
            result.append(TotalRatingNums(id = rating.id,
                                          name=rating.name,
                                          value=int(rating.num_of_rating),
                                          color=rating.color,
                                          textValue=rating.name))
        return QualityAnalyticResponse(
            totalData={
                "total_rating": {
                    "name": "total number of ratings",
                    "value": total_nums_rating,
                    "description": "Общее  количество оценок"
                },
                "total_calls": {
                    'name': 'callsCount',
                    'value': total_call,
                    'description': 'Количество звонков'
                }
            },
            data=result
        )
    @staticmethod
    def _fill_empty_data(status_data: dict, analytic_data: Union[DisposalAnalytic, AntAnalytic]):
        data = [dict(row) for row in analytic_data]
        existed_statuses = [row['name'] for row in data]
        for code in status_data.keys():
            if code not in existed_statuses:
                data.append({'name': code, 'textValue': '00:00:00', 'value': 0})
        for item in data:
            item.update({
                'description': status_data[item['name']]['description'],
                'color': status_data[item['name']]['color']
            })
        return data

    def _get_total_data_for_ant(self, ant_data: list[dict], user_id: int, beginning, ending):
        ant_data = self._convert_all_values_to_timedelta(data=ant_data)
        total_sec = sum(int(item['value'].total_seconds()) for item in ant_data)
        avg_sec = round(total_sec / len(ant_data))
        phone_number = self._inner_phones_repository.get_phone_by_id(user_id=user_id)
        if phone_number is None:
            phone_number = []
        calls_count = self._repository.get_call_count(phone_number=phone_number, beginning=beginning, ending=ending)
        return {
            'data': ant_data,
            'totalData': [
                {
                    'name': 'averageTime',
                    'value': self._convert_from_sec_to_text_format(sec=avg_sec),
                    'description': 'Среднее время (АНТ)'
                },
                {
                    'name': 'sumTime',
                    'value': self._convert_from_sec_to_text_format(sec=total_sec),
                    'description': 'Суммарное время (АНТ)'
                },
                {
                    'name': 'callsCount',
                    'value': calls_count,
                    'description': 'Количество звонков'
                }
            ]
        }

    def _get_total_data_for_disposal(self, disposal_data: list[dict]):
        disposal_data = self._convert_all_values_to_timedelta(data=disposal_data)
        total_time_sec = sum(int(item['value'].total_seconds()) for item in disposal_data)
        break_time_sec = sum(
            int(item['value'].total_seconds()) for item in disposal_data if item['name'].startswith('break'))
        return {
            'data': disposal_data,
            'totalData': [
                {
                    'name': 'totalTime',
                    'value': self._convert_from_sec_to_text_format(sec=total_time_sec),
                    'description': 'Общее время'
                },
                {
                    'name': 'breakTime',
                    'value': self._convert_from_sec_to_text_format(sec=break_time_sec),
                    'description': 'Общее время перерыва'
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

    @staticmethod
    def _convert_all_values_to_timedelta(data: dict):
        for item in data:
            if not isinstance(item['value'], timedelta):
                item['value'] = timedelta(seconds=item['value'])
        return data
