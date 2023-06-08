from datetime import datetime, timedelta, timezone
from app.database.repository.super import NotFoundError
from app.database import QueueStatistics
from .queue_base_model import QueueLoadResponseParams, PeriodsActiveQueue, PeriodsLoadQueue, QueueActiveResponse
from hashlib import md5

__all__ = ["QueueStatisticsService"]

# Количество частей на которое делиться временной отрезок
BREAK_TIME_INTERVAL = 6

tz = timezone(timedelta(hours=3), "MSK")

queue_load_event_map = {
    "ABANDON": "error",
    "EXITEMPTY": "error",
    "RINGNOANSWER": "no_answer",
    "COMPLETEAGENT": "successful",
    "COMPLETECALLER": "successful"
}


class Periods:
    
    DAY = 24/BREAK_TIME_INTERVAL
    HOUR = 60/BREAK_TIME_INTERVAL
    HALF_HOUR = 30/BREAK_TIME_INTERVAL
    WEEKS = 7//BREAK_TIME_INTERVAL
    DATE = datetime.now(tz=tz)

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
            "WEEKS": cls.__calculate_date_days
        }
        if name.upper() in calculate_map:
            return calculate_map[name.upper()](number)
        
        raise NotFoundError(entity_message="Period calculate not found", entity_description="Заданный период вычесления не найден") 

class QueueStatisticsService:
    def __init__(self, queue_statistics_repository: QueueStatistics):
        self._stat:QueueStatistics = queue_statistics_repository
    
    def queue_load(self, uuid: str, type_period: PeriodsLoadQueue):
        period=self._generate_period(type_period.value)
        result_select = self._stat.loading_the_queue(queue_uuid=uuid, period=(",".join(period[0])))
        hash_table_params = {}
        result = []
        for raw_select in result_select:
            hash_key = md5("{}{}".format(str(raw_select.start), str(raw_select.end)).encode()).hexdigest()
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
            )
            for result_select in params:
                if result_select['event'] in queue_load_event_map:
                    param_event = queue_load_event_map[result_select['event']]
                    setattr(param, param_event, result_select['total'])
            result.append(param)
        hash_table_params = None
        result_select = None
        result.sort(key=lambda elem: elem.time_at)
        return result
    
    def active_queues(self, type_period: PeriodsActiveQueue):
        type_period = type_period.value.upper()
        calculate_map = {
            "DAY": 24,
            "HOUR": 60,
            "HALF_HOUR": 30,
            "WEEKS": 7
        }
        if type_period not in calculate_map:
            raise NotFoundError(entity_message="Period calculate not found", entity_description="Заданный период вычесления не найден")
        
        select_raw = self._stat.active_queue(Periods.calculate(type_period, calculate_map[type_period]), Periods.DATE)
        result = []
        for queue in select_raw:
            print(queue.queue_name, queue.total_online, queue.total, queue.total_online // queue.total)
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