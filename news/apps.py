from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    # def ready(self):


import news.signals

# from .tasks import send_mails
# from .scheduler import appointment_scheduler
# print('started')

# appointment_scheduler.add_job(
#     id='mails',
#     func=send_mails,
#     trigger='interval',
#     seconds=10,
# )
# appointment_scheduler.start()



