from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from typing import Callable
from datetime import datetime


class QueueStatistics:
    def __init__(self, session_asterisk: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_asterisk = session_asterisk

    def active_queue(self, start_date: datetime, end_date: datetime):
        query = '''
            SELECT count(src) total_online , COUNT(qm.membername) total, qm.queue_name, IFNULL(q.description, qm.queue_name) description FROM queue_members qm 
            left join (
                SELECT src FROM ps_status_history psh
                JOIN ps_auths pa ON psh.uuid = pa.uuid 
                JOIN queue_members qm2 on pa.id = qm2.membername
                WHERE psh.status_code = 'ready' and psh.time_at BETWEEN :start AND :end
                GROUP BY qm2.membername, psh.status_code
            ) online on qm.membername = online.src
            LEFT JOIN queues q ON qm.queue_name = q.name 
            GROUP BY qm.queue_name
        '''
        with self.session_asterisk() as session:
            res = session.execute(query, params={"start": start_date, "end": end_date}).all()
            return res
    
    def loading_the_queue(self, queue_uuid: str, period: str):
        with self.session_asterisk() as session:
            create_temporary_table = self.__create_temporary_table(queue_uuid, period)
            select = self.__select_loading_the_queue(queue_uuid=queue_uuid)
            for query in create_temporary_table:
                session.execute(query)
            session.commit()
            res = session.execute(select).all()
            session.close()
            return res

    def queue_stat(self, uuid: str, statuses: str, start_date: datetime = None, end_date: datetime = None):
        """ Получение статистики для очереди """
        condition_date = f"AND ql.event in ({statuses}) "
        if start_date and end_date:
            condition_date = condition_date + f"AND (ql.time >= \"{str(start_date)}\" AND ql.time <= \"{str(end_date)}\")"
        query = f'''
                SELECT event, count(event) cnt_calls, sum(call_time) total_time FROM ({self.__query_static_calls().format(condition_date)}) total_queue_calls
                GROUP BY event
            '''
        with self.session_asterisk() as session:
            select = session.execute(query, {"uuid": uuid}).all()
            return select

    @staticmethod
    def __query_static_calls() -> str:
        query = '''
            SELECT ql.event, (ql.data1 + ql.data2) call_time  FROM queue_log ql 
            JOIN queues q ON ql.queuename = q.name
            WHERE q.uuid = :uuid and ql.callid != "NONE" 
            AND (ql.event != "ENTERQUEUE" and ql.event != "CONNECT")
            {}
            GROUP BY ql.callid
            ORDER BY ql.`time` DESC
        '''

        return query

    @staticmethod
    def __create_temporary_table(name: str, values: str) -> str:
        """ Создание временной таблицы с uuid пользователя\n
            Будет служить для формирования выборки во временой прямой
        """
        return [
            "DROP TEMPORARY TABLE IF EXISTS `{}`;".format(name),
            "CREATE TEMPORARY TABLE IF NOT EXISTS `{}`(start datetime, end datetime);".format(name),
            "INSERT INTO `{name}`(start, end) VALUES {values};".format(name=name, values=values)
        ]
    
    def __select_loading_the_queue(self, queue_uuid: str) -> str:
        query = '''
            select t.start, t.end, ifnull(total_temp.event, "EMPTY") event, ifnull(total_temp.total, 0) total from (
                select `{temp_table}`.start, `{temp_table}`.end,  event, count(event) total from `{temp_table}`
                left join queue_log ql on ql.`time` >= `{temp_table}`.start and ql.`time` <= `{temp_table}`.end
                left join queues q on ql.queuename = q.name 
                where q.uuid = "{q_uuid}"
                group by `{temp_table}`.start, event
            ) total_temp
            right join `{temp_table}` t on total_temp.start = t.start
            order by t.start
        '''
        return query.format(temp_table=queue_uuid, q_uuid=queue_uuid)