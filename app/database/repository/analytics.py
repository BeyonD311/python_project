from contextlib import AbstractContextManager
from datetime import date

from sqlalchemy.orm import Session
from typing import Callable


class AnalyticsRepository:
    def __init__(self, session_asterisk: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_asterisk = session_asterisk

    def get_disposal_analytic(self, uuid: str, calculation_method: str, beginning: date, ending: date):
        subquery = '''
                        SELECT status_code, {} delta_time
                        FROM ps_status_history
                        WHERE (status_code LIKE "break%" OR status_code = "ready") AND uuid = :uuid 
                        AND DATE(time_at) BETWEEN :beginning AND :ending
                        GROUP BY status_code
                                        '''
        return self._get_analytic_by_subquery(subquery=subquery,
                                              uuid=uuid,
                                              calculation_method=calculation_method,
                                              beginning=beginning,
                                              ending=ending)

    def get_ant_analytic(self, uuid: str, calculation_method: str, beginning: date, ending: date):
        subquery = '''
                        SELECT status_code, {} delta_time
                        FROM ps_status_history
                        WHERE status_code IN ('precall', 'aftercall', 'externalcall', 'callwaiting') 
                        AND uuid = :uuid AND DATE(time_at) BETWEEN :beginning AND :ending
                        GROUP BY status_code
                                '''
        return self._get_analytic_by_subquery(subquery=subquery,
                                              uuid=uuid,
                                              calculation_method=calculation_method,
                                              beginning=beginning,
                                              ending=ending)

    def get_call_analytic(self, number: str, beginning: date, ending: date):
        with self.session_asterisk() as session:
            query = '''
                        SELECT disposition, (COUNT(src) + COUNT(dst)) call_count
                        FROM cdr
                        WHERE src = :number OR dst = :number AND disposition IN ('ANSWERED', 'NO ANSWER', 'BUSY') 
                        AND DATE(calldate) BETWEEN :beginning AND :ending
                        GROUP BY disposition
            '''
            return session.execute(query, {'number': number, 'beginning': beginning, 'ending': ending}).fetchall()

    def _get_analytic_by_subquery(self, subquery: str, uuid: str, calculation_method: str, beginning: date,
                                  ending: date):
        with self.session_asterisk() as session:
            if calculation_method == 'SUM':
                method = 'SUM(IFNULL(delta_time, 0))'
            elif calculation_method == 'AVG':
                method = 'AVG(IFNULL(delta_time, 0))'
            else:
                raise ValueError(f'{calculation_method} method is not supported')
            subquery = subquery.format(method)
            query = f'''
                        SELECT status_code, TIME_FORMAT(SEC_TO_TIME(delta_time), "%H:%i:%s") delta_time
                        FROM ({subquery}) utils
                                            '''
            result = session.execute(query, {'uuid': uuid, 'beginning': beginning, 'ending': ending}).fetchall()
            return result
