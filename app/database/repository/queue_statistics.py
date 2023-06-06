from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from typing import Callable


class QueueStatistics:
    def __init__(self, session_asterisk: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_asterisk = session_asterisk

    def loading_the_queue(self, queue_uuid: str, period):
        query = self._create_temporary_table(queue_uuid)

    @staticmethod
    def _create_temporary_table(name: str, values: str) -> str:
        """ Создание временной таблицы с uuid пользователя\n
            Будет служить для формирования выборки во временой прямой
        """
        query = '''
            DROP TEMPORARY TABLE {name}

            CREATE TEMPORARY TABLE IF NOT EXISTS {name}(start datetime, end datetime)

            INSERT INTO {name}(start, end)
            VALUES {values}

            {select}
        '''
        query.format(name=name, values=values)

        print(query)

        return query
    
