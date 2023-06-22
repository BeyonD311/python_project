import re
from contextlib import AbstractContextManager
from datetime import date
from sqlalchemy.orm import Session
from typing import Callable


class AnalyticsRepository:
    def __init__(self, session_asterisk: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_asterisk = session_asterisk

    def get_disposal_analytic(self, uuid: str, calculation_method: str, beginning: date, ending: date):
        subquery = '''
                        SELECT status_code, [delta_time]
                        FROM ps_status_history
                        WHERE (status_code LIKE "break%" OR status_code = "ready") AND uuid = :uuid 
                        AND (time_at >= :beginning AND time_at <= :ending)
                        GROUP BY status_code
                                        '''
        fields_replace = {
            "delta_time": {
                "query": "IFNULL(delta_time, 0)",
                "alias": "delta_time"
            }
        }
        subquery = self._calculation_method(subquery, calculation_method, fields_replace)
        return self._get_analytic_by_subquery(subquery=subquery,
                                              uuid=uuid,
                                              beginning=beginning,
                                              ending=ending)

    def get_ant_analytic(self, uuid: str, calculation_method: str, beginning: date, ending: date):
        subquery = '''
                        SELECT status_code, [delta_time]
                        FROM ps_status_history
                        WHERE status_code IN ('precall', 'aftercall', 'externalcall', 'callwaiting') 
                        AND uuid = :uuid AND (time_at >= :beginning AND time_at <= :ending)
                        GROUP BY status_code
                                '''
        fields_replace = {
            "delta_time": {
                "query": "IFNULL(delta_time, 0)",
                "alias": "delta_time"
            }
        }
        subquery = self._calculation_method(subquery, calculation_method, fields_replace)
        return self._get_analytic_by_subquery(subquery=subquery,
                                              uuid=uuid,
                                              beginning=beginning,
                                              ending=ending)

    def get_call_analytic(self, phones: list, beginning: date, ending: date):
        with self.session_asterisk() as session:
            phone = ",".join(phones)
            query = '''
                        SELECT name, SUM(total) value, SUM(total) textValue FROM (
                            SELECT disposition as name, COUNT(src) total
                            FROM cdr
                            WHERE src in (:phone) AND disposition IN ('ANSWERED', 'NO ANSWER', 'BUSY') 
                            AND (calldate >= :beginning and calldate <= :ending) AND lastapp = 'Dial'
                            GROUP BY disposition
                            UNION
                            SELECT disposition as name, COUNT(dst) total
                            FROM cdr
                            WHERE dst in (:phone) AND disposition IN ('ANSWERED', 'NO ANSWER', 'BUSY') 
                            AND (calldate >= :beginning and calldate <= :ending) AND lastapp = 'Dial'
                            GROUP BY disposition
                        ) total_sum
                        GROUP BY name
            '''
            return session.execute(query, {'phone': phone, 'beginning': beginning, 'ending': ending}).fetchall()

    def get_call_quality_assessment(self, phones: list, calculation_method: str, beginning: date, ending: date):
        phones = ",".join(phones)
        with self.session_asterisk() as session:
            query = '''
                SELECT q.id, q.name, [num_of_rating], q.color from (
                    SELECT id_qualities FROM quality_control
                    WHERE quality_control.operator_num in (:phones) AND
                    (quality_control.calldate >= :beginning and quality_control.calldate <= :ending)
                    AND quality_control.id_qualities != 0
                ) qc
                RIGHT JOIN qualities q on qc.id_qualities = q.id
                GROUP BY q.id 
            '''
            fields_replace = {
                "num_of_rating": {
                    "query": "IF(qc.id_qualities is NULL, 0, 1)",
                    "alias": "num_of_rating"
                }
            }
            query = self._calculation_method(query, calculation_method.upper(),fields_replace)
            return session.execute(query, {'phones': phones, 'beginning': beginning, 'ending': ending}).all()

    def _get_analytic_by_subquery(self, subquery: str, uuid: str, beginning: date,
                                  ending: date):
        with self.session_asterisk() as session:
            query = f'''
                        SELECT status_code as name, TIME_FORMAT(SEC_TO_TIME(delta_time), "%H:%i:%s") as textValue,
                        SEC_TO_TIME(delta_time) as value
                        FROM ({subquery}) utils
                                            '''
            result = session.execute(query, {'uuid': uuid, 'beginning': beginning, 'ending': ending}).fetchall()
            return result
        
    def _calculation_method(self,query: str, method: str, field_calculate: dict) -> str:
        """ Опеределение метода расчета SUM или AVG \n
            **field_calculate - описание map \n
                                {
                                    "искомая строка для замены: {
                                        "query": на что меняем
                                        "alias": присвоение имени
                                    }
                                }
        """
        if method != 'SUM' and method != 'AVG':
            raise ValueError(f'{method} method is not supported')
        result = query
        for field, value in field_calculate.items():
            field = f'\[{field}\]'
            result  = re.sub(field, f"{method}({value['query']}) {value['alias']}", query)
        return result
    
    def get_call_count(self, phone_number: list,  beginning: date, ending: date):
        with self.session_asterisk() as session:
            phones = ",".join(phone_number)
            query = '''
                        SELECT sum(total) total FROM (
                            SELECT count(*) total FROM cdr
                            WHERE src in (:phone_number) AND 
                            (calldate >= :beginning AND calldate <= :ending) AND lastapp = 'Dial'
                            UNION ALL
                            SELECT count(*) total FROM cdr
                            WHERE dst in (:phone_number) AND 
                            (calldate >= :beginning AND calldate <= :ending) AND lastapp = 'Dial'
                        ) total_calls
            '''
            result = session.execute(query, {'phone_number': phones, "beginning": beginning.__format__("%Y-%m-%d %H:%M:%S"), "ending": ending.__format__("%Y-%m-%d %H:%M:%S")}).first()
            return result.total
