
from app.database import QueueStatistics

__all__ = ["QueueStatisticsService"]

class QueueStatisticsService:
    def __init__(self, queue_statistics_repository: QueueStatistics):
        self._stat:QueueStatistics = queue_statistics_repository