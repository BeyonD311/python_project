from celery import Celery
from main import container

celery_app = Celery(broker='redis://redis:6379/0')

schedule_service = container.schedule_service()


@celery_app.task(name='check_queue')
def check_queue():
    names = [data[0] for data in schedule_service.get_all_queue_names()]
    for name in names:
        if schedule_service.is_active_now(queue_name=name):
            schedule_service.turn_on_queue(queue_name=name)
            print(f'Queue(name={name}) is turned on')
        else:
            schedule_service.turn_off_queue(queue_name=name)
            print(f'Queue(name={name}) is turned off')


celery_app.conf.beat_schedule = {
    'add-update-every-5-minutes': {
        'task': 'check_queue',
        'schedule': 10.0
    },
}
