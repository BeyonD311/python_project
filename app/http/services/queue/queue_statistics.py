from datetime import datetime, timedelta, timezone
from app.database.repository.super import NotFoundError
from app.database import QueueStatistics, Asterisk
from .queue_base_model import (
    QueueLoadResponseParams, PeriodsActiveQueue, PeriodsLoadQueue, QueueActiveResponse,
    QueueTotalOptions, QueueTotalOptionsParams, QueueTotalStat
    )
from hashlib import md5

__all__ = ["QueueStatisticsService"]

# Количество частей на которое делиться временной отрезок
BREAK_TIME_INTERVAL = 6

queue_load_event_map = {
    "ABANDON": "error",
    "EXITEMPTY": "error",
    "RINGNOANSWER": "no_answer",
    "EXITWITHTIMEOUT": "no_answer",
    "COMPLETEAGENT": "successful",
    "COMPLETECALLER": "successful",
}


class Periods:
    
    DAY = 24/BREAK_TIME_INTERVAL
    HOUR = 60/BREAK_TIME_INTERVAL
    HALF_HOUR = 30/BREAK_TIME_INTERVAL
    WEEK = 7//BREAK_TIME_INTERVAL
    DATE = datetime.now()

    @classmethod
    def __calculate_date_hour(cls, hour: int):
        """ Вычитание от текущего времени переданное количество часов """
        return cls.DATE - timedelta(hours=hour)
    
    @classmethod
    def __calculate_date_min(cls, min: int):
        """ Вычитание от текущего времени переданное количество часов """
        return cls.DATE - timedelta(minutes=min)
    
    @classmethod
    def __calculate_date_days(cls, days: int):
        """ Вычитание от текущего времени переданное количество дней """
        return cls.DATE - timedelta(days=days)
    
    @classmethod
    def __calculate_date_seconds(cls, seconds: int):
        """ Вычитание от текущего времени переданное количество секунд """
        return cls.DATE - timedelta(seconds=seconds)
    
    @classmethod
    def get_interval(cls, name: str) -> int:
        if name.upper() in cls.__dict__:
            return cls.__dict__[name.upper()]
        raise NotFoundError(entity_message="Period not found", entity_description="Заданный период не найден") 
    
    @classmethod
    def calculate(cls, name: str, number: int):
        """ 
        Keyword arguments:
        name -- period calculate\n
        number -- the difference to be subtracted\n
        """
        calculate_map = {
            "DAY": cls.__calculate_date_hour,
            "HOUR": cls.__calculate_date_min,
            "HALF_HOUR": cls.__calculate_date_min,
            "WEEK": cls.__calculate_date_days,
            "SECONDS": cls.__calculate_date_seconds
        }

        if name.upper() in calculate_map:
            return calculate_map[name.upper()](number)
        
        raise NotFoundError(entity_message="Period calculate not found", entity_description="Заданный период вычесления не найден") 

class QueueStatisticsService:
    def __init__(self, queue_statistics_repository: QueueStatistics, asterisk: Asterisk):
        self._stat:QueueStatistics = queue_statistics_repository
        self._asterisk: Asterisk = asterisk
        Periods.DATE = datetime.now()
    
    def __fill_result_total_stat(self, comparison_statuses: dict, raw_select) -> dict:
        result = (QueueTotalOptions()).dict()
        total_calls = 0
        total_time_calls = 0
        calculate_params = {}
        events_time_millisecond = ('RINGCANCELED', 'RINGNOANSWER')
        for param in raw_select:
            total_calls = total_calls + param.cnt_calls
            call_time = param.total_time
            if param.event in events_time_millisecond:
                call_time = call_time / 1000
            if param.event in comparison_statuses:
                if comparison_statuses[param.event] in calculate_params:
                    calculate_params[comparison_statuses[param.event]] = calculate_params[comparison_statuses[param.event]] + param.cnt_calls
                else:
                    calculate_params[comparison_statuses[param.event]] = param.cnt_calls
            total_time_calls = total_time_calls + call_time
        for key in result:
            result[key] = QueueTotalOptionsParams()
        for param, value in calculate_params.items():
            result[param] = QueueTotalOptionsParams(
                    value=value,
                    percent=int((value / total_calls) * 100)
                )
        result['calls'] = QueueTotalOptionsParams(
            percent=100,
            value=total_calls
        )
        avg_time_calls = 0
        percent = 100
        if total_time_calls != 0:
            avg_time_calls = total_time_calls / total_calls
        result['average_talk_time'] = QueueTotalOptionsParams(
            percent=percent,
            value=avg_time_calls
        )

        return QueueTotalOptions(**result)
    
    def total_stat_queue(self, uuid, seconds: int):
        self._asterisk.get_queue_by_uuid(uuid)
        #Сопоставление статусов таблицы и 
        comparison_statuses = {
            "EXITEMPTY": "calls_not_received",
            "EXITWITHTIMEOUT": "calls_not_received",
            "RINGNOANSWER": "calls_not_received",
            "COMPLETECALLER": "received_calls",
            "COMPLETEAGENT": "received_calls",
            "ABANDON": "calls_with_errors",
            "RINGCANCELED": "calls_with_errors",
            "SYSCOMPAT": "calls_with_errors"
        }
        end = Periods.DATE + timedelta(minutes=30)
        start = Periods.calculate("SECONDS", seconds)
        find_statuses = []
        for status in comparison_statuses:
            find_statuses.append(f"\'{status}\'")
        total_select = self._stat.queue_stat(uuid=uuid, statuses=",".join(find_statuses))
        period = self._stat.queue_stat(uuid=uuid, statuses=",".join(find_statuses), start_date=start, end_date=end)
        return QueueTotalStat(
            total=self.__fill_result_total_stat(comparison_statuses=comparison_statuses, raw_select = total_select),
            period=self.__fill_result_total_stat(comparison_statuses=comparison_statuses, raw_select = period)
        )
        
    def queue_load(self, uuid: str, type_period: PeriodsLoadQueue):
        self._asterisk.get_queue_by_uuid(uuid)
        period=self._generate_period(type_period.value)
        result_select = self._stat.loading_the_queue(queue_uuid=uuid, period=(",".join(period[0])))
        hash_table_params = {}
        result = []
        for raw_select in result_select:
            hash_key = md5("{}{}".format(str(raw_select.start.__format__("%Y-%m-%d %H:%M:%S")), 
                                         str(raw_select.end.__format__("%Y-%m-%d %H:%M:%S"))).encode()).hexdigest()
            if hash_key not in hash_table_params:
                hash_table_params[hash_key] = []
            hash_table_params[hash_key].append({
                "event": raw_select.event,
                "start": raw_select.start,
                "total": raw_select.total
            })
        for key, params in hash_table_params.items():
            param = QueueLoadResponseParams(
                time_at=period[1][key]['start'].__format__("%H:%M")
            ).dict()
            for result_select in params:
                if result_select['event'] in queue_load_event_map:
                    param_event = queue_load_event_map[result_select['event']]
                    param[param_event] = param[param_event] + result_select['total']
            result.append(QueueLoadResponseParams(**param))
        hash_table_params = None
        result_select = None
        return result
    
    def active_queues(self, type_period: PeriodsActiveQueue):
        type_period = type_period.value.upper()
        calculate_map = {
            "DAY": 24,
            "HOUR": 60,
            "HALF_HOUR": 30,
            "WEEK": 7
        }
        if type_period not in calculate_map:
            raise NotFoundError(entity_message="Period calculate not found", entity_description="Заданный период вычесления не найден")
        
        select_raw = self._stat.active_queue(Periods.calculate(type_period, calculate_map[type_period]), Periods.DATE)
        result = []
        for queue in select_raw:
            percentage_of_activity = (queue.total_online / queue.total) * 100
            loading_status = "unloaded"
            if percentage_of_activity >= 60:
                loading_status = "loaded"
            result.append(QueueActiveResponse(
                name = queue.description,
                value=percentage_of_activity,
                type=loading_status,
                group=queue.description
            ))
        return result

        

    def _generate_period(self, type_period: str) -> list:
        end = Periods.DATE
        result = []
        hast_table = {}
        period_data = Periods.get_interval(type_period)
        for i in range(BREAK_TIME_INTERVAL):
            start = Periods.calculate(type_period, period_data * (i+1))
            start_s = start.__format__("%Y-%m-%d %H:%M:%S")
            end_s = end.__format__("%Y-%m-%d %H:%M:%S")
            hast_table[md5("{}{}".format(start_s,end_s).encode()).hexdigest()] = {
                "start": start,
                "end": end
            }
            data_values = "(\"{}\", \"{}\")".format(start_s, end_s)
            end = start
            result.append(data_values)
        return result, hast_table