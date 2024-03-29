import logging, asyncio
from main import create_container
from app.http.services.ssh import scp_asterisk_conn
from celery import Celery

celery_app = Celery(broker='redis://redis:6379/0')

schedule_service = create_container().schedule_service()
redis = create_container().redis_pool()


log_file = 'log/CeleryBeat.log'
log_level = logging.FATAL

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(log_level)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Добавляем файловый обработчик к логгеру Celery Beat
beat_logger = logging.getLogger('celery.beat')
beat_logger.addHandler(file_handler)
beat_logger.setLevel(log_level)


@celery_app.task(name='check_queue')
def check_queue():
    names = [data[0] for data in schedule_service.get_all_queue_names()]
    for name in names:
        if schedule_service.is_active_now(queue_name=name):
            schedule_service.turn_on_queue(queue_name=name)
        else:
            schedule_service.turn_off_queue(queue_name=name)


async def download_audio_asterisk():
    _redis = await redis
    while await _redis.llen('download_file_asterisk')!=0:
        file_download =await _redis.rpop('download_file_asterisk')
        await scp_asterisk_conn(file_download)

@celery_app.task(name='download_audio_asterisk')
def download():
    asyncio.run(download_audio_asterisk())
  


celery_app.conf.beat_schedule = {
    'add-update-every-5-minutes': {
        'task': 'check_queue',
        'schedule': 10.0
    },
    'add-every-10-seconds': {
        'task': 'download_audio_asterisk',
        'schedule': 10.0
    }
}